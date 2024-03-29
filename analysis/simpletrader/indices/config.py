from datetime import timedelta

from django.db import models

from simpletrader.kucoin.models import SpotMarket, FuturesContract

class Type(models.IntegerChoices):
    spot_trade_entropy = 1
    futures_trade_entropy = 2
    spot_candle = 3
    futures_candle = 4

def get_task_names(task_type):
    name = Type._value2member_map_[task_type].name
    return {
        'hp': f'kucoin_index.hp_compute.{name}',
        'lp': f'kucoin_index.lp_compute.{name}',
    }

periods = [
    timedelta(seconds=30),
    timedelta(minutes=1),
    timedelta(minutes=2),
    timedelta(minutes=5),
    timedelta(minutes=10),
]

periods_map = {
    Type.spot_trade_entropy: periods,
    Type.futures_trade_entropy: periods,
    Type.spot_candle: periods,
    Type.futures_candle: periods,
}

params_map = {
    Type.spot_trade_entropy: [
        {'price_rounding_factor': 10,},
    ],
    Type.futures_trade_entropy: [
        {'price_rounding_factor': 10,},
    ],
    Type.spot_candle: [{},],
    Type.futures_candle: [{},],
}

related_ids_map = {
    Type.spot_trade_entropy: SpotMarket.objects.all().values_list('id', flat=True),
    Type.futures_trade_entropy: FuturesContract.objects.all().values_list('id', flat=True),
    Type.spot_candle: SpotMarket.objects.all().values_list('id', flat=True),
    Type.futures_candle: FuturesContract.objects.all().values_list('id', flat=True),
}
