from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField


class Market(models.Model):
    base_asset = models.CharField(max_length=8)
    quote_asset = models.CharField(max_length=8)

    @property
    def symbol(self):
        return self.base_asset + self.quote_asset

    def __str__(self):
        return self.symbol


class Order(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='6 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_bid = models.BooleanField()

    def __str__(self):
        return f'{self.market.symbol} {self.time}'


class Trade(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='1 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_buyer_maker =models.BooleanField()
