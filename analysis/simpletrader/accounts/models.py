from uuid import uuid4
from decimal import Decimal

from django.db import models
from django.core.cache import cache
from django.utils.timezone import now

from timescale.db.models.fields import TimescaleDateTimeField
from simpletrader.analysis.models import Asset, Exchange


class Account(models.Model):
    class Types(models.IntegerChoices):
        demo = 10
        regular = 20
        internal = 30
        external = 40

    uid = models.UUIDField(primary_key=True, default=uuid4)
    type = models.IntegerField(choices=Types.choices, default=Types.demo,)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    description = models.TextField(default='')


    def save(self, *args, **kwargs) -> None:
        from simpletrader.demo_accounts_matchers.nobitex import RELOAD_ACCOUNTS_CACHE_KEY
        try:
            cache.incr(RELOAD_ACCOUNTS_CACHE_KEY)
        except ValueError as _:
            cache.set(RELOAD_ACCOUNTS_CACHE_KEY, 1)
        return super().save(*args, **kwargs)

    def get_wallet(self, asset_id: int):
        w = Wallet.objects.filter(
            account_uid=self.uid,
            asset_id=asset_id,
        ).first()
        if not w:
            # Simply returning return value of `create`
            # or `get_or_create_` will cause serialization error.
            Wallet.objects.create(
                account_uid=self.uid,
                asset_id=asset_id,
            )
            return self.get_wallet(asset_id)
        return w


class Wallet(models.Model):
    account_uid = models.UUIDField(db_index=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    free_balance = models.DecimalField(max_digits=32, decimal_places=16, default=0)
    blocked_balance = models.DecimalField(max_digits=32, decimal_places=16, default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_bot_asset_pair',
                fields=('account_uid', 'asset'),
            ),
        )

    def create_transaction(self, type: int, amount: Decimal) -> 'Transaction':
        update_kwargs = {}
        if type in [Transaction.Type.block, Transaction.Type.add_to_blocked_balance]:
            update_kwargs['blocked_balance'] = models.F('blocked_balance') + amount
        if type in [Transaction.Type.block, Transaction.Type.subtract_from_free_balance]:
            update_kwargs['free_balance'] = models.F('free_balance') - amount

        Wallet.objects.filter(pk=self.pk).update(**update_kwargs)
        return Transaction.objects.create(
            type=type,
            wallet=self,
            amount=amount,
        )


class Transaction(models.Model):
    class Type(models.IntegerChoices):
        add_to_blocked_balance = 10
        subtract_from_free_balance = 11
        block = 30

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    created_at = TimescaleDateTimeField(interval='10 day', default=now)
    type = models.SmallIntegerField(choices=Type.choices)
    amount = models.DecimalField(max_digits=32, decimal_places=16, default=0)
