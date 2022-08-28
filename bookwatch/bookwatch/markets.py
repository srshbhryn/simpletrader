
class Market:
    def __init__(self, id: str, symbol: str) -> None:
        self.id = id
        self.symbol = symbol

nobitex_markets = [
    Market('1', 'BTCIRT'),
    Market('2', 'BTCUSDT'),
]

kucoin_spot_markets = [
    Market('3', 'BTC-USDT'),
    Market('4', 'ETH-USDT'),
]

kucoin_futures_markets = [
    Market('5', 'XBTUSDTM'),
    Market('6', 'ETHUSDTM'),
]
