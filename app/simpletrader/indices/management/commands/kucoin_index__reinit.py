
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from simpletrader.indices.config import Type, periods_map, params_map, related_ids_map
from simpletrader.indices.models import Measure, Measurement


class Command(BaseCommand):

    def handle(self, *args, **options):
        self._reload_indices()
        self._reinit_management_tasks()

    def _reload_indices(self):
        self.stdout.write(self.style.WARNING('Reiniting measures...'))
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
            measure, created = Measure.objects.get_or_create(**index)
            description = f'Measure {Type._value2member_map_[measure.type].name} '
            description += f'with period \'{measure.period}\', '
            description += f'with related_id \'{measure.related_id}\', '
            description += f'with params \'{measure.params}\', '
            if created:
                self.stdout.write(description + ', has been CREATED.')
            else:
                self.stdout.write(description + ', already EXISTS')
        self.stdout.write(self.style.SUCCESS('Reiniting measures: DONE'))

    def _reinit_management_tasks(self):
        self.stdout.write(self.style.WARNING('Reiniting tasks...'))
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5,
            period='seconds',
        )
        for type in Type:
            task_key = 'kucoin_index.manage.fire_recent'
            name = task_key + ' for ' + Type._value2member_map_[type].name
            periodic_task = PeriodicTask.objects.filter(
                name=name,
                task=task_key,
            ).first()
            if periodic_task:
                if periodic_task.interval == schedule:
                    self.stdout.write(f'Task Already exists: \'{name}\'.')
                else:
                    periodic_task.interval = schedule
                    periodic_task.save()
                    self.stdout.write(f'Task schedule changed: \'{name}\'.')
            else:
                PeriodicTask.objects.create(
                    name=name,
                    task=task_key,
                    interval=schedule,
                    args=f'[{type}]',
                    start_time = timezone.now(),
                )
                self.stdout.write(f'Task created: \'{name}\'.')
        self.stdout.write(self.style.SUCCESS('Reiniting tasks: DONE'))


