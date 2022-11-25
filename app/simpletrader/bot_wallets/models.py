import decimal

from django.db import models
from django.db import transaction
from django.utils import timezone

from timescale.db.models.fields import TimescaleDateTimeField

from simpletrader.trader.models import Bot


class Wallet(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    asset_id = models.SmallIntegerField()
    exchange_id = models.SmallIntegerField()
    free_balance = models.DecimalField(max_digits=32, decimal_places=16, default=decimal.Decimal(0))
    blocked_balance = models.DecimalField(max_digits=32, decimal_places=16, default=decimal.Decimal(0))

    class Meta:
        unique_together = [
            ('bot', 'asset_id', 'exchange_id',),
        ]
        constraints = [
            models.constraints.CheckConstraint(
                name='wallet_non_negative_free_balance',
                check=models.Q(free_balance__gte=0)
            ),
            models.constraints.CheckConstraint(
                name='wallet_non_negative_blocked_balance',
                check=models.Q(blocked_balance__gte=0)
            ),
        ]

    def create_transaction(self, amount: decimal.Decimal, type: int) -> None:
        assert transaction.get_connection().in_atomic_block
        update_kwargs = {
            _WalletTransactionTypes.block: {
                'free_balance': models.F('free_balance') - amount,
                'blocked_balance': models.F('blocked_balance') + amount,
            },
            _WalletTransactionTypes.gain: {
                'free_balance': models.F('free_balance') + amount,
            },
            _WalletTransactionTypes.pay: {
                'blocked_balance': models.F('blocked_balance') - amount,
            },
        }[type]
        Wallet.objects.filter(
            id=self.id,
        ).update(**update_kwargs)
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            type=type,
        )


class _WalletTransactionTypes(models.IntegerChoices):
    block = 1 # free => block
    gain = 2 # `out` => free
    pay = 3 # block => `out`


class WalletTransaction(models.Model):
    Types = _WalletTransactionTypes

    timestamp = TimescaleDateTimeField(default=timezone.now, interval='24 hour')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=32, decimal_places=16)
    type = models.SmallIntegerField()
