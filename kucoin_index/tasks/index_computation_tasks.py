import logging
import datetime


from django.db.models import Q, F, ExpressionWrapper, FloatField, Sum

from kucoin_data.models import SpotMarket, FuturesContract, SpotTrade, FuturesTrade
from kucoin_index.models import Measurement, Measure
from kucoin_index.utils import Round, entropy, register_task
from kucoin_index.config import Type

log = logging.getLogger('django')


@register_task(Type.spot_trade_entropy)
def compute_spottrade_entropy(measure_id, time):
    time = datetime.datetime.fromisoformat(time)
    measure = Measure.objects.get(pk=measure_id)
    related_id = measure.related_id
    period = measure.period
    price_rounding_factor = measure.params['price_rounding_factor']
    normal_price_rounding_factor = price_rounding_factor * SpotMarket.objects.get(pk=related_id).price_increment
    values = SpotTrade.objects.filter(
        market_id=related_id,
        time__lt=time,
        time__gte=time-period,
    ).annotate(rounded_price=ExpressionWrapper(Round(
        F('price') / normal_price_rounding_factor,
            output_field=FloatField(),
        ),
        output_field=FloatField(),
    )).values('rounded_price').annotate(
        volume_sum=Sum('volume'),
        is_buyer_maker_volume_sum=Sum('volume', filter=Q(is_buyer_maker=True)),
        is_seller_maker_volume_sum=Sum('volume', filter=Q(is_buyer_maker=False)),
    )
    volume_sums = []
    is_buyer_maker_volume_sums = []
    is_seller_maker_volume_sums = []
    for value in values:
        volume_sums.append(value['volume_sum'])
        is_buyer_maker_volume_sums.append(value['is_buyer_maker_volume_sum'])
        is_seller_maker_volume_sums.append(value['is_seller_maker_volume_sum'])
    Measurement.objects.create(
        measure_id=measure_id,
        time=time,
        values={
            'e':entropy(volume_sums),
            'be':entropy(is_buyer_maker_volume_sums),
            'se':entropy(is_seller_maker_volume_sums),
        },
    )


@register_task(Type.futures_trade_entropy)
def compute_futurestrade_entropy(measure_id, time):
    time = datetime.datetime.fromisoformat(time)
    measure = Measure.objects.get(pk=measure_id)
    related_id = measure.related_id
    period = measure.period
    price_rounding_factor = measure.params['price_rounding_factor']
    normal_price_rounding_factor = price_rounding_factor * FuturesContract.objects.get(pk=related_id).tick_size
    values = FuturesTrade.objects.filter(
        market_id=related_id,
        time__lt=time,
        time__gte=time-period,
    ).annotate(rounded_price=ExpressionWrapper(Round(
        F('price') / normal_price_rounding_factor,
            output_field=FloatField(),
        ),
        output_field=FloatField(),
    )).values('rounded_price').annotate(
        volume_sum=Sum('volume'),
        is_buyer_maker_volume_sum=Sum('volume', filter=Q(is_buyer_maker=True)),
        is_seller_maker_volume_sum=Sum('volume', filter=Q(is_buyer_maker=False)),
    )
    volume_sums = []
    is_buyer_maker_volume_sums = []
    is_seller_maker_volume_sums = []
    for value in values:
        volume_sums.append(value['volume_sum'])
        is_buyer_maker_volume_sums.append(value['is_buyer_maker_volume_sum'])
        is_seller_maker_volume_sums.append(value['is_seller_maker_volume_sum'])
    Measurement.objects.create(
        measure_id=measure_id,
        time=time,
        values={
            'e':entropy(volume_sums),
            'be':entropy(is_buyer_maker_volume_sums),
            'se':entropy(is_seller_maker_volume_sums),
        },
    )
