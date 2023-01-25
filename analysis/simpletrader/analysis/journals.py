
from simpletrader.base.journals import Journal, AsyncJournal
from simpletrader.analysis.models import Trade


class TradeJournal(Journal):
    class Meta:
        model = Trade


class AsyncTradeJournal(AsyncJournal):
    class Meta:
        model = Trade
