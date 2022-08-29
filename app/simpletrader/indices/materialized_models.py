
from django.db import models

from simpletrader.kucoin.models import Market


class BaseMeasure(models.Model):
    start_time = models.DateTimeField()
    period = models.DurationField()
    market = models.ForeignKey(Market, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class CandleStick_05m(BaseMeasure):
    min = models.FloatField()
    max = models.FloatField()
    open = models.FloatField()
    close = models.FloatField()

    class Meta:
        managed = False
        db_table = 'indices_candlestick_05m'
