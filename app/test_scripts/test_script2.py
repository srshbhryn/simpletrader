def main():
    import datetime
    import matplotlib.pyplot as plt

    from django.db.models import Min, Max, Avg, F, Sum, Q, ExpressionWrapper, FloatField

    from timescale.db.models import TimeBucket, Last, First

    from simpletrader.base.db import Round
    from simpletrader.indices.utils import entropy
    from simpletrader.kucoin_test.tools import judge_strategy_0
    from simpletrader.kucoin.models import SpotTrade, SpotMarket, Asset, FuturesTrade, FuturesContract


    market = SpotMarket.objects.filter(
        base_asset=Asset.btc,
        quote_asset=Asset.usdt,
    ).first()
    first_time = SpotTrade.objects.filter(market=market).aggregate(ft=Min('time'))['ft']
    def get_success_rate(interval_minutes, rounding_factor, market, first_time, last_time):
        interval = datetime.timedelta(minutes=interval_minutes)
        trades = SpotTrade.objects.filter(
            market=market,
            time__gte=first_time,
            time__lte=last_time,
        )
        price_averages = trades.annotate(
            bucket=TimeBucket('time', interval),
            value=F('price')*F('volume'),
        ).values('bucket').annotate(
            min_price=Min('price'),
            max_price=Max('price'),
            first_price=First('price', 'bucket'),
            last_price=Last('price', 'bucket'),
            value_sum=Sum('value'),
            volume_sum=Sum('volume'),
            bm_value_sum=Sum('value', filter=Q(is_buyer_maker=True)),
            bm_volume_sum=Sum('volume', filter=Q(is_buyer_maker=True)),
            sm_value_sum=Sum('value', filter=Q(is_buyer_maker=False)),
            sm_volume_sum=Sum('volume', filter=Q(is_buyer_maker=False)),
        ).annotate(
            avg_price=F('value_sum')/F('volume_sum'),
            bm_avg_price=F('bm_value_sum')/F('bm_volume_sum'),
            sm_avg_price=F('sm_value_sum')/F('sm_volume_sum'),
        ).values_list(
            'bucket',
            'bm_avg_price',
            'sm_avg_price',
            'bm_volume_sum',
            'sm_volume_sum',
            'avg_price',
            'min_price',
            'max_price',
            'first_price',
            'last_price',
        )
        times, bm_avg_prices, sm_avg_prices, bm_volume_sum, sm_volume_sum, avg_prices, \
            min_prices, max_prices, first_prices, last_prices = zip(*list(price_averages))
        bm_volume_sum = list(map(lambda v: v or 0, bm_volume_sum))
        sm_volume_sum = list(map(lambda v: v or 0, sm_volume_sum))
        bm_avg_prices = list(map(lambda v: v or 0, bm_avg_prices))
        sm_avg_prices = list(map(lambda v: v or 0, sm_avg_prices))
        min_prices = list(map(lambda v: v or 0, min_prices))
        max_prices = list(map(lambda v: v or 0, max_prices))
        first_prices = list(map(lambda v: v or 0, first_prices))
        last_prices = list(map(lambda v: v or 0, last_prices))
        # entropies
        normal_price_rounding_factor = rounding_factor * market.price_increment
        values = trades.annotate(rounded_price=ExpressionWrapper(Round(
            F('price') / normal_price_rounding_factor,
                output_field=FloatField(),
            ),
            output_field=FloatField(),
        ), bucket=TimeBucket('time', interval),).values('rounded_price', 'bucket').annotate(
            volume_sum=Sum('volume'),
            bm_volume_sum=Sum('volume', filter=Q(is_buyer_maker=True)),
            sm_volume_sum=Sum('volume', filter=Q(is_buyer_maker=False)),
        ).values('bucket', 'volume_sum', 'bm_volume_sum', 'sm_volume_sum')

        for k, _ in enumerate(values):
            values[k]['bucket'] = values[k]['bucket']
        volume_sums = {t: [] for t in times}
        bm_volume_sums = {t: [] for t in times}
        sm_volume_sums = {t: [] for t in times}
        for value in values:
            volume_sums[value['bucket']].append(value['volume_sum'])
            bm_volume_sums[value['bucket']].append(value['bm_volume_sum'])
            sm_volume_sums[value['bucket']].append(value['sm_volume_sum'])
        bm_entropies = []
        sm_entropies = []
        entropies = []
        for t in times:
            entropies.append(entropy(volume_sums[t]))
            bm_entropies.append(entropy(bm_volume_sums[t]))
            sm_entropies.append(entropy(sm_volume_sums[t]))
        u = {}
        d = {}
        for a in [1,-1]:
            for b in [1, -1]:
                u[(a, b,)] = 0
                d[(a, b,)] = 0
        init_balance = 100000
        balance = init_balance
        num_trades = 0
        for i in range(4, len(times)-4):
            eds = round(entropies[i] - sm_entropies[i])
            edb = round(entropies[i] - bm_entropies[i])

            side = None
            # import random
            # if random.randrange(100) >= 25:
            #     continue
            # if random.randrange(2):
            #     side = 'short'
            # else:
            #     side = 'long'

            # cond1 = avg_prices[i] < avg_prices[i-1]
            cond2 = eds > 0 and edb < 0
            cond3 = eds < 0 and edb > 0
            # if not (cond2 or cond3):
            #     continue
            # if cond1 and cond3:
            #     side = 'short'
            # if not cond1 and cond2:
            #     side = 'long'

            # if cond1:
            #     side = 'short'
            # else:
            #     side = 'long'

            if cond3:
                side = 'short'
            if cond2:
                side = 'long'


            if side is None:
                continue
            num_trades += 1

            change_factor = 1.015
            tp_price = last_prices[i] * change_factor
            sl_price = last_prices[i] / change_factor
            if side == 'short':
                tp_price, sl_price = sl_price, tp_price
            trade_amount = (balance * .8)/avg_prices[i]
            _balance = balance * .8
            balance -= balance * .8
            try:
                pnl = judge_strategy_0(
                    market=market,
                    amount=trade_amount,
                    side=side,
                    entry_time=times[i]+interval,
                    tp_price=tp_price,
                    sl_price=sl_price,
                    max_exit_time=times[i]+2*interval,
                )
                balance += pnl + _balance
            except:
                balance += _balance
        return balance / init_balance
        # return (
        #     (u[(1, -1)] + d[(-1, 1)] - u[(-1, 1)] + d[(1, -1)]) /
        #     (sum([v for _, v in u.items()]) + sum([v for _, v in d.items()]))
        # )
    data = {}
    rounding_factors = [10]
    # rounding_factors = [1400, 1750, 2000, 2300, 2600]
    # rounding_factors = [1900, 1925, 1950, 1975, 2000, 2025, 2050, 2075, 2100]
    # rounding_factors = [2000 + i for i in range(-10, 11)]
    markets = SpotMarket.objects.all()
    # markets = SpotMarket.objects.filter(base_asset=Asset.ada)
    # rounding_factors = [500, 1000, 2000]
    rounding_factors = [150, 200, 300]
    # rounding_factors = [5, 10, 15, 20, 50, 100]
    test_hours = 1
    total_hours = 24 * 6
    interval_minutes = 2
    for market in markets:
    # for market in SpotMarket.objects.filter(base_asset=Asset.btc):
        data[market.symbol] = {}
        for rounding_factor in rounding_factors:
            data[market.symbol][rounding_factor] = []
            for i in range(0, int(total_hours / test_hours)):
                start = first_time + datetime.timedelta(hours=test_hours*i)
                end = first_time + datetime.timedelta(hours=test_hours*(i+1))
                avg = get_success_rate(interval_minutes, rounding_factor, market, start, end)
                data[market.symbol][rounding_factor].append(avg)
            results = data[market.symbol][rounding_factor]
            # print(f'{rounding_factor}\t{market.symbol}\n{data[market.symbol][rounding_factor]}')
            print(f'{rounding_factor}\t{market.symbol}\t', end='')
            x = 1
            for _ in results:
                x *= _
            print(f'{sum(results)/len(results)}\t{x}\t{len([r for r in results if r > 1])}\t{len([r for r in results if r < 1])}\t{len(results)}')
            # print(results)
            # print('--------------------')

    # import matplotlib.pyplot as plt
    # x_axis = [i for i in range(len(data[market.symbol][rounding_factors[0]]))]
    # for rf in rounding_factors:
    #     plt.plot(x_axis, data[market.symbol][rf], '-')
    # plt.show()

main()
