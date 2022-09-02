from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField


class Bot(models.Model):
    token = models.BinaryField(max_length=4, unique=True)
    name = models.CharField(max_length=128)


class Account(models.Model):
    exchange = models.IntegerField()
    credentials = models.JSONField()


class BotAccount(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Order(models.Model):
    placed_by = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    exchange_id = models.BigIntegerField(db_index=True)
    client_order_id = models.CharField(db_index=True, max_length=128)
    market = models.IntegerField(db_index=True)
    status = models.IntegerField()
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()


class Fill(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    exchange_id = models.BigIntegerField(db_index=True)
    exchange_order_id = models.BigIntegerField(db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, default=None)
    market = models.IntegerField(db_index=True)
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()
