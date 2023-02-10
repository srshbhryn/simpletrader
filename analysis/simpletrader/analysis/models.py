
from django.db import models
from django.utils.functional import cached_property

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class Asset(models.Model):
    name = models.CharField(max_length=32)


class Exchange(models.Model):
    name = models.CharField(max_length=64)


class OrderStatus(models.Model):
    name = models.CharField(max_length=32)


class Pair(models.Model):
    base_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='+')
    quote_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='+')


class Market(models.Model):
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)

    @cached_property
    def base_asset(self):
        return self.pair.base_asset

    @cached_property
    def quote_asset(self):
        return self.pair.quote_asset


class Trade(models.Model):
    market_id = models.IntegerField()
    time =  TimescaleDateTimeField(interval='6 hour')
    base_amount = models.FloatField()
    quote_amount = models.FloatField()
    is_buyer_maker = models.BooleanField()

    objects = TimescaleManager()
