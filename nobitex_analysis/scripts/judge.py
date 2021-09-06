from django.conf import settings

from nobitex.models import MarketTrades


taker_fee = settings.NOBITEX['FEES']['TAKER']
maker_fee = settings.NOBITEX['FEES']['MAKER']


class Order:
    id = 0
    class OrderType:
        active = 0
        cancelled = 1
        done = 2

    def __init__(self, amount, price):
        Order.id += 1
        self.id = Order.id
        self.amount = amount
        self.price = price


class Judge:
    def __init__(self, market):
        self.market = market
        self.trades = MarketTrades.objects.order_by('time')
        self.orders = []

    def matched_orders(self):
        pass
    
    def incremet_time_until_order_are_matched_or_timeout(self, time):
        
    # trader queries
    def get_trade_status(self, trade_id):
        pass

    def get_latest_trades(self, time_period):
        pass
