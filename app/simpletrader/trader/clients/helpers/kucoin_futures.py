from simpletrader.trader.sharedconfigs import Market


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
