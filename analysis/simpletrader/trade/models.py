from uuid import uuid4

from django.db import models
from django.utils.timezone import now

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

from simpletrader.analysis.models import Asset, Pair, OrderStatus, Exchange
from simpletrader.accounts.models import Account


class Order(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    external_id = models.CharField(max_length=32, db_index=True)
    client_order_id = models.CharField(db_index=True, max_length=128, null=True, default=None)
    leverage = models.SmallIntegerField(default=1)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    timestamp = TimescaleDateTimeField(interval='24 hour', default=now)
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()

    objects = TimescaleManager()


class Fill(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    order_uid = models.UUIDField(db_index=True, null=True, default=None,)
    external_id = models.CharField(max_length=32, db_index=True)
    external_order_id = models.CharField(max_length=32, db_index=True)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    timestamp = TimescaleDateTimeField(interval='24 hour', default=now)
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()
    fee = models.DecimalField(max_digits=32, decimal_places=16)
    fee_asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    objects = TimescaleManager()
