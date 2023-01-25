from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

class Asset(models.Model):
    name = models.CharField(max_length=32)


class Exchange(models.Model):
    name = models.CharField(max_length=64)


class Market(models.Model):
    base_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='+')
    quote_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='+')
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)


class Trade(models.Model):
    market_id = models.IntegerField()
    time =  TimescaleDateTimeField(interval='6 hour')
    base_amount = models.FloatField()
    quote_amount = models.FloatField()
    is_buyer_maker = models.BooleanField()

    objects = TimescaleManager()

    # class Meta:
    #     managed = True
