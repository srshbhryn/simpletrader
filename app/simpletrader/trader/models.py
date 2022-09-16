from django.db import models
import uuid
from django.utils.functional import cached_property

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

from simpletrader.trader.clients import get_client
from simpletrader.trader.sharedconfigs import Exchange

def create_bot_token():
    return uuid.uuid4().hex[:4]


class Bot(models.Model):
    token = models.CharField(max_length=4, primary_key=True, default=create_bot_token)
    name = models.CharField(max_length=128)

    def get_client(self, exchange_id):
        return get_client(exchange_id, self.token)

class Account(models.Model):
    exchange_id = models.IntegerField()
    credentials = models.JSONField()

    @cached_property
    def exchange_name(self):
        return Exchange.get_by('id', self.exchange_id).name


class BotAccount(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    @classmethod
    def get_bot_credentials(cls, exchange_id, bot_token):
        account = cls.objects.get(
            bot__token=bot_token,
            account__exchange_id=exchange_id,
        ).account
        return account.credentials

    class Meta:
        unique_together = [
            ['bot', 'account',],
        ]


class Order(models.Model):
    placed_by = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    #
    exchange_id = models.CharField(max_length=32, db_index=True)
    client_order_id = models.CharField(db_index=True, max_length=128, null=True, blank=True, default=None)
    leverage = models.SmallIntegerField(default=1, blank=True)
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
    #
    exchange_id = models.CharField(max_length=32, db_index=True)
    exchange_order_id = models.CharField(max_length=32, db_index=True)
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
