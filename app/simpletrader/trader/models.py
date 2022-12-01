from typing import Dict
from functools import cache
import json
import string

from django.db import models
import uuid
from django.utils.functional import cached_property
from django.contrib.postgres import constraints
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators


from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

from simpletrader.trader.clients import get_client
from simpletrader.trader.sharedconfigs import Exchange

from .clients.base import BaseClient


def number_to_base(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def create_bot_token():
    return uuid.uuid4().hex[:16]


class Bot(models.Model):
    name = models.CharField(max_length=128)
    managed = models.BooleanField(default=False)

    @property
    def token(self):
        digits = string.digits + string.ascii_letters
        indices = number_to_base(self.id, len(digits))
        return ''.join([
            digits[i]
            for i in indices
        ])


    def get_client(self, exchange_id: int) -> BaseClient:
        return get_client(exchange_id, self.token)

    _bots: Dict[str, 'Bot'] = {}

    @classmethod
    def get(cls, token: str) -> 'Bot':
        if not token in cls._bots:
            cls._bots[token] = Bot.objects.get(token=token)
        return cls._bots[token]

    @cache
    def account(self, exchange_id: int) -> 'Account':
        return BotAccount.objects.get(
            bot__token=self.token,
            account__exchange_id=exchange_id,
        ).account


class AccountManager(models.Manager):
    def create(self, exchange_id, _credentials):
        return super().create(exchange_id, json.dumps(_credentials))


class Account(models.Model):
    def __init__(self, id=None, exchange_id=None, _credentials=None) -> None:
        super().__init__(id=id, exchange_id=exchange_id, _credentials=json.dumps(_credentials))
    exchange_id = models.SmallIntegerField(db_index=True)
    _credentials = models.TextField(default='{}')

    @property
    def credentials(self):
        return json.loads(json.loads(self._credentials))

    @credentials.setter
    def credentials(self, value):
        self._credentials = json.dumps(value)

    @cached_property
    def exchange_name(self):
        return Exchange.get_by('id', self.exchange_id).name

    objects = AccountManager()


class BotAccount(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Order(models.Model):
    placed_by = models.ForeignKey(Bot, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    #
    external_id = models.CharField(max_length=32, db_index=True)
    client_order_id = models.CharField(db_index=True, max_length=128, null=True, blank=True, default=None)
    leverage = models.SmallIntegerField(default=1, blank=True)
    exchange_id = models.IntegerField(db_index=True)
    market_id = models.IntegerField(db_index=True)
    status_id = models.IntegerField()
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()

    objects = TimescaleManager()


class Fill(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    #
    external_id = models.CharField(max_length=32, db_index=True)
    external_order_id = models.CharField(max_length=32, db_index=True)
    exchange_id = models.IntegerField(db_index=True)
    market_id = models.IntegerField(db_index=True)
    timestamp = TimescaleDateTimeField(interval='24 hour')
    price = models.DecimalField(max_digits=32, decimal_places=16, default=None, null=True)
    volume = models.DecimalField(max_digits=32, decimal_places=16)
    is_sell = models.BooleanField()
    fee = models.DecimalField(max_digits=32, decimal_places=16)
    fee_asset_id = models.IntegerField()

    objects = TimescaleManager()


class WalletSnapShot(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    #
    timestamp = TimescaleDateTimeField(interval='24 hour')
    asset_id = models.SmallIntegerField(db_index=True)
    free_balance = models.DecimalField(max_digits=32, decimal_places=16)
    blocked_balance = models.DecimalField(max_digits=32, decimal_places=16)

    objects = TimescaleManager()
