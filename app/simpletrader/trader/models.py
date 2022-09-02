from django.db import models

from simpletrader.base.models import Exchange
from timescale.db.models.fields import TimescaleDateTimeField


class Bot(models.Model):
    name = models.CharField(max_length=128)

class Account(models.Model):
    exchange = models.IntegerField()
    credentials = models.JSONField()


class BotAccount(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

class Order(models.Model):
    market = models.IntegerField()
    status = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.FloatField(default=None, null=True)
    volume = models.FloatField()
    is_sell = models.BooleanField()
