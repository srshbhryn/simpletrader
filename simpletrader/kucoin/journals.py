from simpletrader.base.journals import Journal
from simpletrader.kucoin.models import SpotOrderBook, SpotTrade, FuturesOrderBook, FuturesTrade

class SpotOrderBookJournal(Journal):
    class Meta:
        model = SpotOrderBook


class SpotTradeJournal(Journal):
    class Meta:
        model = SpotTrade


class FuturesOrderBookJournal(Journal):
    class Meta:
        model = FuturesOrderBook


class FuturesTradeJournal(Journal):
    class Meta:
        model = FuturesTrade

