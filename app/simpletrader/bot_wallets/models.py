import decimal

from django.db import models
from django.db import transaction
from django.utils import timezone

from simpletrader.trader.models import Bot


class Wallet(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    asset_id = models.SmallIntegerField()
    exchange_id = models.SmallIntegerField()
    free_balance = models.DecimalField(max_digits=32, decimal_places=16, default=decimal.Decimal(0))
    blocked_balance = models.DecimalField(max_digits=32, decimal_places=16, default=decimal.Decimal(0))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unqibotassetexchange',
                fields=('bot', 'asset_id', 'exchange_id',),
            ),
            models.CheckConstraint(
                name='walletnonnefreebalance',
                check=models.Q(free_balance__gte=0)
            ),
            models.CheckConstraint(
                name='walletnonnegblockedbalance',
                check=models.Q(blocked_balance__gte=0)
            ),
        ]

    def create_transaction(self, amount: decimal.Decimal, type: int) -> 'WalletTransaction':
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
        return WalletTransaction.objects.create(
            parent_id=(
                self.transactions.order_by('-id').values('id').first()
                or {}
            ).get('id'),
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

    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=32, decimal_places=16)
    type = models.SmallIntegerField(choices=Types.choices)
    parent = models.OneToOneField('self', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                name='one_null_parent_only',
                condition=models.Q(parent_id__isnull=True),
                fields=['wallet_id'],
            )
        ]
