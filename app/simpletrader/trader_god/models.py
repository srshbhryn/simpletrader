import uuid

from django.db import models
from django.utils import timezone

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

from simpletrader.trader.models import Bot


class BotSummary(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    from_timestamp = TimescaleDateTimeField(interval='24 hour')
    to_timestamp = models.DateTimeField()
    is_demo = models.BooleanField(default=True)
    initial_worth = models.DecimalField(max_digits=32, decimal_places=16)
    final_worth = models.DecimalField(max_digits=32, decimal_places=16)

    objects = TimescaleManager()

    class Meta:
        indexes = [
            models.Index(
                name='a8408d602e31e4934a51d4154',
                fields=('bot', '-from_timestamp',),
                include=('to_timestamp',),
            ),
        ]


class _BotStateChangeStates(models.IntegerChoices):
    created = 0
    stopped = 1
    pre_stop = 2
    demo_running = 10
    real_running = 11


class BotStateChange(models.Model):
    States = _BotStateChangeStates

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    parent = models.OneToOneField('self', null=True, blank=True, on_delete=models.PROTECT)
    state = models.SmallIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_bot_state(cls, bot_id):
        return (cls.objects.filter(
            bot_id=bot_id,
        ).order_by(
            '-created_at',
        ).values('state').first() or {}).get('state')

    class Meta:
        indexes = [
            models.Index(
                name='a39e3f290edc1428eb43052a4',
                fields=('bot', '-created_at',),
                include=('state',),
            ),
        ]

class DummyOrder(models.Model):
    exchange_id = models.SmallIntegerField(db_index=True)
    external_id = models.CharField(max_length=32, db_index=True)

    @classmethod
    def create(cls, exchange_id):
        external_id = uuid.uuid4().hex
        cls.objects.create(
            exchange_id=exchange_id,
            external_id=external_id,
        )
