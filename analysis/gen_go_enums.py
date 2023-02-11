def main():
    from simpletrader.analysis.models import Asset, Exchange, OrderStatus, Pair, Market
    fid = open('../bots/lib/config/assets/assets.go', 'w')
    fid.write('package assets\n\n')
    fid.write('func Load() {}\n\n')
    fid.write('type Asset int64\n\n')
    fid.write('const (\n')
    assets = Asset.objects.all()
    for a in assets:
        if a.name == '1inch':
            a.name = 'oneinch'

    first = True
    for asset in assets:
        fid.write(f'\t{asset.name.upper()} {"Asset" if first else ""} = {asset.id}\n')
        first = False
    fid.write(')\n\n')
    fid.write(f'var ALL = [{len(assets)}]Asset{{\n')
    for asset in assets:
        fid.write(f'\t{asset.name.upper()},\n')
    fid.write('}')
    fid.close()

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

    fid = open('../bots/lib/config/exchanges/exchanges.go', 'w')
    fid.write('package exchanges\n\n')
    fid.write('func Load() {}\n\n')
    fid.write('type Exchange int64\n\n')
    fid.write('const (\n')
    exchanges = Exchange.objects.all()

    first = True
    for exchange in exchanges:
        fid.write(f'\t{to_camel_case(exchange.name)} {"Exchange" if first else ""} = {exchange.id}\n')
        first = False
    fid.write(')\n\n')
    fid.write(f'var ALL = [{len(exchanges)}]Exchange{{\n')
    for exchange in exchanges:
        fid.write(f'\t{to_camel_case(exchange.name)},\n')
    fid.write('}')
    fid.close()

    fid = open('../bots/lib/config/orderstates/orderstates.go', 'w')
    fid.write('package orderstates\n\n')
    fid.write('func Load() {}\n\n')
    fid.write('type OrderState int64\n\n')
    fid.write('const (\n')
    states = OrderStatus.objects.all()
    first = True
    for state in states:
        fid.write(f'\t{to_camel_case(state.name)} {"OrderState" if first else ""} = {state.id}\n')
        first = False
    fid.write(')\n\n')
    fid.write(f'var ALL = [{len(states)}]OrderState{{\n')
    for state in states:
        fid.write(f'\t{to_camel_case(state.name)},\n')
    fid.write('}')
    fid.close()

    fid = open('../bots/lib/config/pairs/pairs.go', 'w')
    fid.write('package pairs\n\n')
    fid.write('func Load() {}\n\n')
    fid.write('''type Pair struct {
            Id int64
            BaseAsset  assets.Asset
            QuoteAsset assets.Asset
        }
        ''')

    fid.write('var (\n')
    pairs = Pair.objects.all()
    first = True
    for p in pairs:
        pair_name = to_camel_case(p.base_asset.name + '_' + p.quote_asset.name)
        base = p.base_asset.name.upper()
        quote = p.quote_asset.name.upper()
        fid.write(f'\t{pair_name} {"Pair" if first else ""} = Pair{{{p.id},assets.{base},assets.{quote}}}\n')
        first = False
    fid.write(')\n\n')

    fid = open('../bots/lib/config/markets/markets.go', 'w')
    fid.write('package markets\n\n')
    fid.write('func Load() {}\n\n')
    fid.write('''type Market struct {
            id int64
            pair  pairs.Pair
            exchange exchanges.Exchange
        }
        ''')

    fid.write('var (\n')
    markets = Market.objects.all()
    first = True
    for m in markets:
        market_name = to_camel_case(m.exchange.name + '_' + m.pair.base_asset.name + '_' + m.pair.quote_asset.name)
        pair_name = to_camel_case(m.pair.base_asset.name + '_' + m.pair.quote_asset.name)
        exchange = to_camel_case(m.exchange.name)
        fid.write(f'\t{market_name} {"Market" if first else ""} = Market{{{m.id},pairs.{pair_name},exchanges.{exchange}}}\n')
        first = False
    fid.write(')\n\n')


main()