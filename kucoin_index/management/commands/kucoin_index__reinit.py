
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from kucoin_index.config import Type, periods_map, params_map, related_ids_map
from kucoin_index.models import Measure, Measurement


class Command(BaseCommand):

    def handle(self, *args, **options):
        self._reload_indices()
        self._reinit_management_tasks()

    def _reload_indices(self):
        indices = []
        for type in Type:
            for period in periods_map[type]:
                for params in params_map[type]:
                    for related_id in related_ids_map[type]:
                        indices.append({
                            'type': type,
                            'period': period,
                            'related_id': related_id,
                            'params': params,
                        })
        for index in indices:
            _, created = Measure.objects.get_or_create(**index)
            #print things...

    def _reinit_management_tasks(self):
        return
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
