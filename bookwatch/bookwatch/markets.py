from bookwatch.sharedconfigs import MARKETS, Exchange

class WatchMarket:
    def __init__(self, id: str, symbol: str) -> None:
        self.id = id
        self.symbol = symbol

nobitex_markets = [
    WatchMarket(str(m.id), m.symbol)
    for m in MARKETS
    if m.exchange == Exchange.get_by('name', 'nobitex')
]

kucoin_spot_markets = [
    WatchMarket(str(m.id), m.symbol)
    for m in MARKETS
    if m.exchange == Exchange.get_by('name', 'kucoin_spot')
]

kucoin_futures_markets = [
    WatchMarket(str(m.id), m.symbol)
    for m in MARKETS
    if m.exchange == Exchange.get_by('name', 'kucoin_futures')
]
