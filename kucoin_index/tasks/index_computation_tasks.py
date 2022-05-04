import logging

from celery import shared_task

from django.db.models import Q, F, ExpressionWrapper, FloatField, Sum

from kucoin_data.models import SpotMarket, FuturesContract, SpotTrade, FuturesTrade
from kucoin_index.models import Measurement, Measure
from kucoin_index.utils import Round, entropy

log = logging.getLogger('django')


@shared_task('kucoin_index.compute.spottrade_entropy')
def compute_spottrade_entropy(measure_id, time):
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
    )).values('is_buyer_maker', 'rounded_price').annotate(
        volume_sum=Sum('volume'),
        is_buyer_maker_volume_sum=Sum('volume', filter=Q(is_buyer_maker=True)),
        is_seller_maker_volume_sum=Sum('volume', filter=Q(is_buyer_maker=False)),
    )
    volume_sums = []
    is_buyer_maker_volume_sums = []
    is_seller_maker_volume_sums = []
    for value in values:
        if value['volume_sum'] is not None:
            volume_sums.append(value['volume_sum'])
        if value['is_buyer_maker_volume_sum'] is not None:
            is_buyer_maker_volume_sums.append(value['is_buyer_maker_volume_sum'])
        if value['is_seller_maker_volume_sum'] is not None:
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


@shared_task('kucoin_index.compute.futurestrade_entropy')
def compute_futurestrade_entropy(related_id, period, price_rounding_factor):
    log.info('CALLED futurestrade_entropy')
