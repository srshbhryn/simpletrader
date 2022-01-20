
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from kucoin_data.models import Asset, SpotMarket, FuturesContract


class Command(BaseCommand):

    def handle(self, *args, **options):
            self._reinit_assets()
            self._reinit_markets()
            self._reinit_tasks()

    def _reinit_assets(self):
        self.stdout.write(self.style.WARNING('Reiniting assets...'))
        for spot_name, futures_name in settings.KUCOIN['ASSETS']:
            _, is_created = Asset.objects.get_or_create(
                spot_name=spot_name,
                futures_name=futures_name,
            )
            if is_created:
                self.stdout.write(f'Asset\'{spot_name}\'|\'{futures_name}\' added.')
            else:
                self.stdout.write(f'Asset\'{spot_name}\'|\'{futures_name}\' already exists.')
        self.stdout.write(self.style.SUCCESS('Reiniting assets: DONE.'))

    def _reinit_markets(self):
        self.stdout.write(self.style.WARNING('Reiniting Spot Markets...'))
        for base_name, quote_name in settings.KUCOIN['SPOT_MARKETS']:
            base_asset = Asset.objects.get(spot_name=base_name)
            quote_asset = Asset.objects.get(spot_name=quote_name)
            if base_asset is None or quote_asset is None:
                raise CommandError(f'Invalid Spot Market pair: ({base_name},{quote_name}).')
            _, is_created = SpotMarket.objects.get_or_create(
                base_asset=base_asset,
                quote_asset=quote_asset,
            )
            if is_created:
                self.stdout.write(f'Added Spot Market\'{base_name}-{quote_name}\'.')
            else:
                self.stdout.write(f'Spot Market\'{base_name}-{quote_name}\' already exists.')
        self.stdout.write(self.style.SUCCESS('Reiniting Spot Markets: DONE'))
        self.stdout.write(self.style.WARNING('Reiniting Futures Contracts...'))
        for base_name, quote_name in settings.KUCOIN['FUTURES_CONTRACTS']:
            base_asset = Asset.objects.get(futures_name=base_name)
            quote_asset = Asset.objects.get(futures_name=quote_name)
            if base_asset is None or quote_asset is None:
                raise CommandError(f'Invalid Futures Contract pair: ({base_name},{quote_name}).')
            _, is_created = FuturesContract.objects.get_or_create(
                base_asset=base_asset,
                quote_asset=quote_asset,
            )
            if is_created:
                self.stdout.write(f'Added Futures Contract\'{base_name}-{quote_name}\'.')
            else:
                self.stdout.write(f'Futures Contract\'{base_name}-{quote_name}\' already exists.')
        self.stdout.write(self.style.SUCCESS('Reiniting Futures Contracts: DONE'))

    def _reinit_tasks(self):
        self.stdout.write(self.style.WARNING('Reiniting tasks...'))
        for task_key in [
            # 'kucoin_data.collect.spot_orders',
            'kucoin_data.collect.spot_trades',
        ]:
            for base_name, quote_name in settings.KUCOIN['SPOT_MARKETS']:
                market = SpotMarket.objects.get(
                    base_asset__spot_name=base_name,
                    quote_asset__spot_name=quote_name,
                )
                if market is None:
                    raise CommandError(f'There is no Spot Market {base_name}-{quote_name}')
                args = f'[\"{market.symbol}\", {market.id}]'
                name=task_key + 'for ' + market.symbol
                schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=settings.KUCOIN['TASK_PERIODS'][task_key],
                    period='seconds',
                )
                periodic_task = PeriodicTask.objects.filter(
                    name=name,
                    task=task_key,
                    args=args,
                ).first()
                if periodic_task:
                    if periodic_task.interval == schedule:
                        self.stdout.write(f'Task Already exists: {name}.')
                        continue
                    periodic_task.interval = schedule
                    periodic_task.save()
                    self.stdout.write(f'Task schedule changed: {name}.')
                    continue
                PeriodicTask.objects.create(
                    name=name,
                    task=task_key,
                    interval=schedule,
                    args=args,
                    start_time = timezone.now(),
                )
                self.stdout.write(f'Task Added: {name}.')
        for task_key in [
            # 'kucoin_data.collect.futures_orders',
            'kucoin_data.collect.futures_trades',
        ]:
            for base_name, quote_name in settings.KUCOIN['FUTURES_CONTRACTS']:
                market = FuturesContract.objects.get(
                    base_asset__futures_name=base_name,
                    quote_asset__futures_name=quote_name,
                )
                if market is None:
                    raise CommandError(f'There is no Futures Contract {base_name}{quote_name}')
                args = f'[\"{market.symbol}\", {market.id}]'
                name=task_key + 'for ' + market.symbol
                schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=settings.KUCOIN['TASK_PERIODS'][task_key],
                    period='seconds',
                )
                periodic_task = PeriodicTask.objects.filter(
                    name=name,
                    task=task_key,
                    args=args,
                ).first()
                if periodic_task:
                    if periodic_task.interval == schedule:
                        self.stdout.write(f'Task Already exists: {name}.')
                        continue
                    periodic_task.interval = schedule
                    periodic_task.save()
                    self.stdout.write(f'Task schedule changed: {name}.')
                    continue
                PeriodicTask.objects.create(
                    name=name,
                    task=task_key,
                    interval=schedule,
                    args=args,
                    start_time = timezone.now(),
                )
                self.stdout.write(f'Task Added: {name}.')

            for task_key in ['kucoin_data.store.orders_and_trades',]:
                args = '[]'
                name=task_key
                schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=settings.KUCOIN['TASK_PERIODS'][task_key],
                    period='seconds',
                )
                periodic_task = PeriodicTask.objects.filter(
                    name=name,
                    task=task_key,
                    args=args,
                ).first()
                if periodic_task:
                    if periodic_task.interval == schedule:
                        self.stdout.write(f'Task Already exists: {name}.')
                        continue
                    periodic_task.interval = schedule
                    periodic_task.save()
                    self.stdout.write(f'Task schedule changed: {name}.')
                    continue
                PeriodicTask.objects.create(
                    name=name,
                    task=task_key,
                    interval=schedule,
                    args=args,
                    start_time = timezone.now(),
                )

        self.stdout.write(self.style.SUCCESS('Reiniting tasks: DONE'))
