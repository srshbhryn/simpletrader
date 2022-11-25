from django.db import models
from django.db.models import Q

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

from simpletrader.base.models import assuming
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
    created_at = TimescaleDateTimeField(interval='24 hour')

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
        constraints = [
            models.constraints.CheckConstraint(
                name='a6cb673588bb5404b9f1ce9db',
                check=assuming(
                    Q(parent__isnull=True),
                    then=Q(state=_BotStateChangeStates.created),
                ),
            ),
            models.constraints.CheckConstraint(
                name='f81ab85918df49239d31c9fe',
                check=assuming(
                    Q(parent__state=_BotStateChangeStates.created),
                    then=Q(state=_BotStateChangeStates.demo_running)
                ),
            ),
            models.constraints.CheckConstraint(
                name='',
                check=assuming(
                    Q(parent__state=_BotStateChangeStates.pre_stop),
                    then=Q(state=_BotStateChangeStates.stopped)
                ),
            ),
            models.constraints.CheckConstraint(
                name='a824b3342dcd0481c8e1d4c78',
                check=assuming(
                    Q(parent__state=_BotStateChangeStates.demo_running),
                    then=Q(state=_BotStateChangeStates.real_running)
                    | Q(state=_BotStateChangeStates.pre_stop),
                ),
            ),
            models.constraints.CheckConstraint(
                name='a306c64a823db4c6e81460490',
                check=assuming(
                    Q(parent__state=_BotStateChangeStates.real_running),
                    then=Q(state=_BotStateChangeStates.demo_running)
                ),
            ),
        ]
