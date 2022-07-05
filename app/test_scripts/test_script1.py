def main():
    import datetime
    import matplotlib.pyplot as plt

    from django.db.models import Min, Max, Avg, F, Sum, Q, ExpressionWrapper, FloatField

    from timescale.db.models import TimeBucket, Last, First

    from simpletrader.base.db import Round
    from simpletrader.indices.utils import entropy
    from simpletrader.kucoin.models import SpotTrade, SpotMarket, Asset, FuturesTrade, FuturesContract


    market = SpotMarket.objects.filter(
        base_asset=Asset.btc,
        quote_asset=Asset.usdt,
    ).first()
    first_time = SpotTrade.objects.filter(market=market).aggregate(ft=Min('time'))['ft']
    last_time = first_time + datetime.timedelta(hours=72)
    def get_success_rate(market, first_time, last_time):
        interval = datetime.timedelta(seconds=60)
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
        times = list(map(lambda dt: dt.timestamp(), times))

        # entropies
        normal_price_rounding_factor = 10 * market.price_increment
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
            values[k]['bucket'] = values[k]['bucket'].timestamp()

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
                # for c in [1, -1]:
                    # u[(a, b, c)] = 0
                    # d[(a, b, c)] = 0
                u[(a, b,)] = 0
                d[(a, b,)] = 0
        init_balance = 100000
        balance = init_balance
        num_trades = 0
        for i in range(len(times)-1):
            # pc = round(10000*(avg_price[i+1] / avg_price[i])) / 100
            # # er = round(1000*(bm_entropies[i] / sm_entropies[i] )) / 100
            # pr = round(100_00_00*(bm_avg_prices[i] / sm_avg_prices[i] )) / 100_00
            # vr = round(100_00_00*(bm_volume_sum[i] / sm_volume_sum[i] )) / 100_00
            eds = round(entropies[i] - sm_entropies[i])
            edb = round(entropies[i] - bm_entropies[i])
            # pc -= 100
            # pr -= 100
            # vr -= 100

            def sign(a):
                if a > 0:
                    return 1
                return -1
            # print(
            #     sign(pc),
            #     sign(pr),
            #     sign(vr),
            # )
            # print(
            #     pc,
            #     pr,
            #     vr,
            # )
            # key = (sign(pr), sign(vr), sign(ed))
            # key = (sign(edb), sign(eds), )
            # print(d)
            # print(u)
            # print(key)
            # if sign(pc) == 1:
            #     u[key] += 1
            # else:
            #     d[key] += 1

            # if key in [
            #     (1, 1),
            #     (-1, -1),
            # ]:
            #     continue
            side = None
            # if eds > 0 and edb < 0 and eds - abs(edb) > 0.01:
            #     side = 'long'
            # if eds < 0 and edb > 0 and edb - abs(eds) > 0.01:
            #     side = 'short'
            # if sm_entropies[i] > bm_entropies[i]:
            #     side = 'short'
            #     # side = 'long'
            # else:
            #     side = 'long'


            if eds > 0 and edb < 0:
                side = 'long'

            if eds < 0 and edb > 0:
                side = 'short'


            if side is None:
                continue
            num_trades += 1

            change_factor = 1.015
            fee = 0.006
            entry_price = first_prices[i+1]
            if side == 'long':
                if min_prices[i+1] <= entry_price / change_factor:
                    exit_price = entry_price / change_factor
                elif max_prices[i+1] >= change_factor * entry_price:
                    exit_price = change_factor * entry_price
                else:
                    exit_price = last_prices[i+1]
            if side == 'short':
                if max_prices[i+1] >= change_factor * entry_price:
                    exit_price = change_factor * entry_price
                if min_prices[i+1] <=  entry_price / change_factor:
                    exit_price = entry_price / change_factor
                else:
                    exit_price = last_prices[i+1]
            side_direction = 1 if side == 'long' else -1
            amount = .8 * (balance / avg_prices[i])
            # leverage = 1
            balance -= entry_price * amount * fee
            balance -= exit_price * amount * fee
            balance += side_direction * (exit_price - entry_price) * amount
        # print(
        #     (u[(1, -1)] + d[(-1, 1)] - u[(-1, 1)] + d[(1, -1)]) /
        # (sum([v for _, v in u.items()]) + sum([v for _, v in d.items()]))
        # )
        # print('xxxxxxxx')
        # print(u)
        # print(d)
        # print(sum([v for _, v in u.items()]))
        # print(sum([v for _, v in d.items()]))
        # print(f'{sign(pr-100)}\t{sign(vr-100)}\t{sign(pc-100)}')
        # print(f'{times[i]}\t{bm_entropies[i]}\t{sm_entropies[i]}\t{entropies[i]}\t{avg_price[i]}\t{pc}')
        return (round(100_00*balance / init_balance) / 100_00, num_trades)
        # return (
        #     (u[(1, -1)] + d[(-1, 1)] - u[(-1, 1)] + d[(1, -1)]) /
        #     (sum([v for _, v in u.items()]) + sum([v for _, v in d.items()]))
        # )
    data = {}
    for market in SpotMarket.objects.all():
        data[market.symbol] = []
        for i in range(0,7):
            start = first_time + datetime.timedelta(hours=10*i)
            end = first_time + datetime.timedelta(hours=10*(i+1))
            avg = get_success_rate(market, start, end)
            data[market.symbol].append(avg)
            # print(avg)
    for k, v in data.items():
        print(f'{k}\t{v}')
main()
