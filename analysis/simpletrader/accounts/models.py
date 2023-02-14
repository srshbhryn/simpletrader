from uuid import uuid4
from decimal import Decimal

from django.db import models
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
    type = models.IntegerField(choices=Types.choices)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    description = models.TextField(default='')

    def get_wallet(self, asset_id: int):
        return Wallet.objects.filter(
            account_uid=self.uid,
            asset=asset_id,
        ).first() or Wallet.objects.create(
            account_uid=self.uid,
            asset=asset_id,
        )


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
            models.CheckConstraint(
                name='non_negative_free_balance',
                check=models.Q(free_balance__gte=0),
            ),
            models.CheckConstraint(
                name='non_negative_block_balance',
                check=models.Q(blocked_balance__gte=0),
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

    uuid = models.UUIDField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    created_at = TimescaleDateTimeField(interval='10 day', default=now)
    type = models.SmallIntegerField(choices=Type.choices)
