from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager



class Bot(models.Model):
    token = models.BinaryField(max_length=4, unique=True)
    name = models.CharField(max_length=128)


class Account(models.Model):
    exchange_id = models.IntegerField()
    credentials = models.JSONField()


class BotAccount(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ['bot', 'account',],
        ]


class Order(models.Model):
    placed_by = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    client_order_id = models.CharField(db_index=True, max_length=128)
    market_id = models.IntegerField(db_index=True)
    status_id = models.IntegerField()
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()

    objects = TimescaleManager()

    class Meta:
        managed = False

class Fill(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    exchange_id = models.BigIntegerField(db_index=True)
    exchange_order_id = models.BigIntegerField(db_index=True)
    market_id = models.IntegerField(db_index=True)
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()
    fee = models.DecimalField(max_digits=32, decimal_places=16)
    fee_asset_id = models.IntegerField()

    objects = TimescaleManager()

    class Meta:
        managed = False
