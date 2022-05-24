from simpletrader.base.journals import Journal
from simpletrader.nobitex.models import Order, Trade

class OrderJournal(Journal):
    class Meta:
        model = Order
        rotate_period = 40

class TradeJournal(Journal):
    class Meta:
        model = Trade
