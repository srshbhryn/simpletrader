from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField

from kucoin_index.config import Type

class Measure(models.Model):
    type = models.IntegerField(choices=Type.choices)
    period = models.DurationField()
    related_id = models.IntegerField()
    params = models.JSONField(default=dict)


class Measurement(models.Model):
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)
    timestamp = TimescaleDateTimeField(interval='4 hour')
    values = models.JSONField(default=dict)
