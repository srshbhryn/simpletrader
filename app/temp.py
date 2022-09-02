
def main():
    import json
    from simpletrader.kucoin.models import Market, SpotMarket, FuturesContract, Asset
    from simpletrader.nobitex.models import Market as NbxMarket
    from simpletrader.base.models import Exchange

    markets = []
    for market in Market.objects.all():
        obj = {
            Exchange.nobitex: NbxMarket,
            Exchange.kucoin_spot: SpotMarket,
            Exchange.kucoin_futures: FuturesContract,
        }[market.type].objects.get(pk=market.related_id)
        markets.append({
            "id": market.id,
            "exchange_id": market.type,
            "base_asset_id": obj.base_asset,
            "quote_asset_id": obj.quote_asset,
            "symbol": obj.symbol
        })
    # print(markets)
    print(json.dumps(markets))


main()
