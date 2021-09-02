import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from nobitex.models import Market


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        list_market = settings.NOBITEX['MARKETS']
        active_markets = []
        for asset_name, currency_name in list_market:
            market, _ = Market.objects.get_or_create(
                asset_name = asset_name,
                currency_name = currency_name,
            )
            active_markets.append(market)

        PeriodicTask.objects.filter(
            Q(task__contains='nobitex.tasks.store_market_data') |
            Q(task__contains='nobitex.tasks.collect_market_data')
        ).delete()

        ####  nobitex.tasks.collect_market_data  ####
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every = settings.NOBITEX['TASK_PERIODS']['collect_market_data'],
            period = 'seconds',
        )
        start_time = timezone.now()
        time_offset_step = datetime.timedelta(
            seconds=settings.NOBITEX['TASK_PERIODS']['collect_market_data'] / len(active_markets)
        )

        PeriodicTask.objects.bulk_create([
            PeriodicTask(
                name = f'collecting market data for {market.symbol}',
                task =  'nobitex.tasks.collect_market_data',
                interval = schedule,
                args = f'[\"{market.symbol}\", {market.id}]',
                start_time = start_time + k*time_offset_step,
            )
            for k, market in enumerate(active_markets)
        ])

        ####  nobitex.tasks.store_market_data  ####
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every = settings.NOBITEX['TASK_PERIODS']['store_market_data'],
            period = 'seconds',
        )
        start_time = timezone.now()
        PeriodicTask.objects.create(
            name = f'store market data.',
            task =  'nobitex.tasks.store_market_data',
            interval = schedule,
            args = '[]',
            start_time = start_time,
        )

        self.stdout.write('DONE\n')


