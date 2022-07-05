def main():
    from django.db.models import Min, Max
    from simpletrader.kucoin.models import SpotTrade, SpotMarket, Asset, FuturesTrade, FuturesContract
    import matplotlib.pyplot as plt

    market = SpotMarket.objects.filter(
        base_asset=Asset.btc,
        quote_asset=Asset.usdt,
    ).first()
    min_max_time = SpotTrade.objects.filter(market=market).aggregate(
        min_time=Min('time'),
        max_time=Max('time'),
    )
    print(min_max_time['max_time']-min_max_time['min_time'])

    trades = SpotTrade.objects.filter(
        market=market
    ).values_list('price', 'time')
    prices, times = zip(*list(trades))
    times = list(map(lambda dt: dt.timestamp(), times))

    plt.plot(times, prices, 'b')

    market = FuturesContract.objects.filter(
        base_asset=Asset.btc,
        quote_asset=Asset.usdt,
    ).first()
    trades = FuturesTrade.objects.filter(
        market=market
    ).values_list('price', 'time')
    prices, times = zip(*list(trades))
    times = list(map(lambda dt: dt.timestamp(), times))

    plt.plot(times, prices, 'r')


    plt.show()


main()
