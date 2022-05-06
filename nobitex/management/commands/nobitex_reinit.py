import datetime
import json
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from nobitex.models import Market
from nobitex import configs

class Command(BaseCommand):


    def _reinit_markets(self):
        list_market = configs.MARKETS
        active_markets = []
        for base_asset, quote_asset in list_market:
            market, _ = Market.objects.get_or_create(
                base_asset = base_asset,
                quote_asset = quote_asset,
            )
            active_markets.append(market)
        self.active_markets = active_markets

    def _reinit_tasks(self, task_key):
        tasks = PeriodicTask.objects.filter(
            Q(task__contains=task_key)
        ).all()
        markets_with_tasks_ids = []
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every = configs.TASK_PERIODS[task_key],
            period = 'seconds',
        )
        for task in tasks:
            market_id = json.loads(task.args)[1]
            if market_id in [m.id for m in self.active_markets] and task.interval == schedule:
                markets_with_tasks_ids.append(market_id)
                continue
            task.delete()
        for market in self.active_markets:
            if market.id in markets_with_tasks_ids:
                continue
            args = f'[\"{market.symbol}\", {market.id}]'
            periodic_task = PeriodicTask.objects.filter(
                name = task_key,
                task =  task_key,
                args = args,
            ).first()
            if periodic_task:
                if periodic_task.interval == schedule:
                    continue
                periodic_task.delete()
            time_offset_step = datetime.timedelta(
               seconds=configs.TASK_PERIODS[task_key] / 10
            )
            PeriodicTask.objects.create(
                name = f'{task_key} for {market.symbol}',
                task =  task_key,
                interval = schedule,
                args = args,
                start_time = timezone.now() + time_offset_step*random.randrange(10),
            )

    def handle(self, *args, **kwargs):
        self._reinit_markets()
        self._reinit_tasks('nobitex.collect.orders')
        self._reinit_tasks('nobitex.collect.trades')
        for task_key in ['nobitex.store.orders', 'nobitex.store.trades']:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every = configs.TASK_PERIODS[task_key],
                period = 'seconds',
            )
            periodic_task = PeriodicTask.objects.filter(
                name = task_key,
                task =  task_key,
                args = '[]',
            ).first()
            if periodic_task:
                if periodic_task.interval == schedule:
                    continue
                periodic_task.delete()
            PeriodicTask.objects.create(
                name = task_key,
                task =  task_key,
                interval = schedule,
                args = '[]',
                start_time = timezone.now(),
            )

        self.stdout.write('DONE\n')


