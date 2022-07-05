from simpletrader.base.journals import Journal
from simpletrader.kucoin.models import Trade, SpotTrade, FuturesTrade


class SpotTradeJournal(Journal):
    class Meta:
        model = SpotTrade


class FuturesTradeJournal(Journal):
    class Meta:
        model = FuturesTrade


class TradeJournal(Journal):
    class Meta:
        model = Trade
