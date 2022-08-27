
class Market:
    def __init__(self, id: str, symbol: str) -> None:
        self.id = id
        self.symbol = symbol

nobitex_markets = [
    Market('1', 'BTCIRT'),
    Market('2', 'BTCUSDT'),
]

