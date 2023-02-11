def main():
    from simpletrader.analysis.models import Asset, Exchange, OrderStatus, Pair, Market
    fid = open('../bookwatch/bookwatch/config.py', 'w')
    fid.write('from enum import Enum\n\n\n')
    fid.write('class Asset(Enum):\n')
    assets = Asset.objects.all()
    for a in assets:
        if a.name == '1inch':
            a.name = 'oneinch'
    for asset in assets:
        fid.write(f'\t{asset.name.upper()} = {asset.id}\n')
    fid.write('\n\n')

    def to_camel_case(snake_case):
        camel_case = ''
        should_be_capital = True
        for c in snake_case:
            if c == '_':
                should_be_capital = True
                continue
            camel_case += c.upper() if should_be_capital else c
            should_be_capital = False
        return camel_case

    fid.write('class Exchange(Enum):\n')
    exchanges = Exchange.objects.all()

    for exchange in exchanges:
        fid.write(f'\t{to_camel_case(exchange.name)} = {exchange.id}\n')
    fid.write('\n\n')

    fid.write('class PairType:\n')
    fid.write('\tdef __init__(self, id, base_asset, quote_asset):\n')
    fid.write('\t\tself.id = id\n')
    fid.write('\t\tself.base_asset = base_asset\n')
    fid.write('\t\tself.quote_asset = quote_asset\n')
    fid.write('\n\n')

    fid.write('class Pair(Enum):\n')
    pairs = Pair.objects.all()
    for p in pairs:
        pair_name = to_camel_case(p.base_asset.name + '_' + p.quote_asset.name)
        base = p.base_asset.name.upper()
        quote = p.quote_asset.name.upper()
        fid.write(f'\t{pair_name} = PairType({p.id}, Asset.{base}, Asset.{quote})\n')
    fid.write('\n\n')

    fid.write('class MarketType:\n')
    fid.write('\tdef __init__(self, id, exchange, pair):\n')
    fid.write('\t\tself.id = id\n')
    fid.write('\t\tself.exchange = exchange\n')
    fid.write('\t\tself.pair = pair\n')
    fid.write('\n\n')



    fid.write('class Market(Enum):\n')

    markets = Market.objects.all()
    for m in markets:
        market_name = to_camel_case(m.exchange.name + '_' + m.pair.base_asset.name + '_' + m.pair.quote_asset.name)
        pair_name = to_camel_case(m.pair.base_asset.name + '_' + m.pair.quote_asset.name)
        exchange = to_camel_case(m.exchange.name)
        fid.write(f'\t{market_name} = MarketType({m.id}, Exchange.{exchange}, Pair.{pair_name})\n')
    fid.close()


main()