from datetime import timedelta

from django.db import models

from kucoin_data.models import SpotMarket, FuturesContract

class Type(models.IntegerChoices):
    spot_trade_entropy = 1
    futures_trade_entropy = 2

def get_task_names(task_type):
    name = Type._value2member_map_[task_type].name
    return {
        'hp': f'kucoin_index.hp_compute.{name}',
        'lp': f'kucoin_index.lp_compute.{name}',
    }

entropy_periods = [
    timedelta(minutes=1),
    timedelta(minutes=5),
    timedelta(minutes=30),
    timedelta(hours=1),
    timedelta(hours=4),
    timedelta(hours=12),
    timedelta(hours=24),
]

periods_map = {
    Type.spot_trade_entropy: entropy_periods,
    Type.futures_trade_entropy: entropy_periods,
}

params_map = {
    Type.spot_trade_entropy: [
        {'price_rounding_factor': 10,},
    ],
    Type.futures_trade_entropy: [
        {'price_rounding_factor': 10,},
    ],
}

related_ids_map = {
    Type.spot_trade_entropy: list(SpotMarket.objects.all().values_list('id', flat=True)),
    Type.futures_trade_entropy: list(FuturesContract.objects.all().values_list('id', flat=True)),
}
