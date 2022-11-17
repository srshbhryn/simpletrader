from simpletrader.trader.sharedconfigs import Market, Asset


def get_symbol(market_id: int) -> str:
    symbol: str = Market.get_by('id', market_id).symbol
    symbol = symbol.replace('BTC', 'XBT')
    symbol = symbol.replace('-', '')
    return symbol

def translate_symbol(kucoin_symbol: str) -> str:
    if 'USDTM' not in kucoin_symbol:
        return None
    symbol = kucoin_symbol[:-5] + '-USDT'
    symbol = symbol.replace('XBT', 'BTC')
    return symbol


def get_fee_asset_id(asset_name: str) -> int:
    asset_name = asset_name.lower()
    for name in [
        'usdt',
        'xbt',
    ]:
        return Asset.get_by('name', name).id
    return Asset.get_by('name', asset_name).id
