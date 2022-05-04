from django.core.cache import caches
from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField

from simpletrader.celery import app
from kucoin_index.config import Type, get_task_names

cache = caches['index_manager']


class Measure(models.Model):
    type = models.IntegerField(choices=Type.choices)
    period = models.DurationField()
    related_id = models.IntegerField()
    params = models.JSONField(default=dict)

    @classmethod
    def clean_up_tasks_cache(self):
        pass


class Measurement(models.Model):
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='4 hour')
    values = models.JSONField(default=dict)

    class Meta:
        unique_together = [
            ['measure', 'time',],
        ]

    def save(self, *args, **kwargs):
        if self.pk is None and self.values == {}:
            return
        return super().save(*args, **kwargs)

    @property
    def _task_id(self):
        print(type(self.time))
        print(type(self.time.timestamp()))
        return f'{self.measure_id}_{str(self.time.timestamp()).replace(".", "")}'

    @property
    def is_done(self):
        return Measurement.objects.filter(
            measure=self.measure,
            time=self.time,
        ).exists()

    @property
    def task_status(self):
        result = app.AsyncResult(self._task_id)
        if result is None:
            return None
        return result.state

    def run_task(self, is_high_priority=False):
        task_name = get_task_names(self.measure.type)[
            'hp' if is_high_priority else 'lp'
        ]
        app.send_task(
            name=task_name,
            kwargs={
                'measure_id': self.measure.id,
                'time': self.time.isoformat(),
            },
            task_id=self._task_id,
        )
