from simpletrader.trader.sharedconfigs import Market


def get_symbol(market_id: int) -> str:
    symbol: str = Market.get_by('id', market_id).symbol
    symbol.replace('BTC', 'XBT')
    symbol.replace('USDT', 'USDTM')
    symbol.replace('-', '')
    return symbol
