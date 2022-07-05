def main():
    import datetime
    from django.db.models import Min, Max
    from django.db.models import Min, Max, Avg, F, Sum, Q, ExpressionWrapper, FloatField

    from timescale.db.models import TimeBucket, Last, First

    from simpletrader.base.db import Round
    from simpletrader.indices.utils import entropy
    from simpletrader.kucoin.models import SpotTrade, SpotMarket, Asset, FuturesTrade, FuturesContract
    import matplotlib.pyplot as plt
    interval = datetime.timedelta(minutes=20)
    market = SpotMarket.objects.filter(
        base_asset=Asset.btc,
        quote_asset=Asset.usdt,
    ).first()
    min_max_time = SpotTrade.objects.filter(market=market).aggregate(
        min_time=Min('time'),
        max_time=Max('time'),
    )
    condition = Q(
        Q(time__gte=min_max_time['min_time']) &
        Q(time__lte=min_max_time['min_time'] + datetime.timedelta(days=2))
    )
    print(min_max_time['max_time']-min_max_time['min_time'])

    trades = SpotTrade.objects.filter(
        condition,
    ).values_list('price', 'time')
    prices, times = zip(*list(trades))
    times = list(map(lambda dt: dt.timestamp(), times))
    # plt.plot(times, prices, 'r')

    rounding_factor = 10
    normal_price_rounding_factor = rounding_factor * market.price_increment
    values = SpotTrade.objects.filter(
        condition,
    ).annotate(rounded_price=ExpressionWrapper(Round(
        F('price') / normal_price_rounding_factor,
            output_field=FloatField(),
        ),
        output_field=FloatField(),
    ), bucket=TimeBucket('time', interval),).values('rounded_price', 'bucket').annotate(
        volume_sum=Sum('volume'),
        bm_volume_sum=Sum('volume', filter=Q(is_buyer_maker=True)),
        sm_volume_sum=Sum('volume', filter=Q(is_buyer_maker=False)),
    ).values('bucket', 'volume_sum', 'bm_volume_sum', 'sm_volume_sum')

    buckets = []
    for k, _ in enumerate(values):
        values[k]['bucket'] = values[k]['bucket'].timestamp()
        buckets.append(values[k]['bucket'])
    volume_sums = {t: [] for t in buckets}
    bm_volume_sums = {t: [] for t in buckets}
    sm_volume_sums = {t: [] for t in buckets}
    for value in values:
        volume_sums[value['bucket']].append(value['volume_sum'])
        bm_volume_sums[value['bucket']].append(value['bm_volume_sum'])
        sm_volume_sums[value['bucket']].append(value['sm_volume_sum'])
    bm_entropies = []
    sm_entropies = []
    entropies = []
    for t in buckets:
        entropies.append(entropy(volume_sums[t]))
        bm_entropies.append(entropy(bm_volume_sums[t]))
        sm_entropies.append(entropy(sm_volume_sums[t]))
    plt.plot(buckets, bm_entropies, 'r.')
    plt.plot(buckets, sm_entropies, 'b.')
    plt.plot(buckets, entropies, 'y.')
    plt.show()


main()
