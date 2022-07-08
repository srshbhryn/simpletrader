from simpletrader.base.journals import Journal
from simpletrader.kucoin.models import Trade


class TradeJournal(Journal):
    class Meta:
        model = Trade
