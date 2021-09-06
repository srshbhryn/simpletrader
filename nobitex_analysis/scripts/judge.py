from django.conf import settings

from nobitex.models import MarketTrades



FEE = settings.NOBITEX['FEES']['TAKER']


class Order:
    id = 0
    class OrderStatus:
        active = 0
        cancelled = 1
        done = 2
        pending = 3

    class OrderSide:
        buy = 0
        sell = 1

    def __init__(self, amount, price, side):
        Order.id += 1
        self.id = Order.id
        self.amount = amount
        self.price = price
        self.status = Order.OrderStatus.active
        self.side = side

    @property
    def is_active(self):
        return self.status == Order.OrderStatus.active

    @property
    def is_pending(self):
        return self.status == Order.OrderStatus.pending


class Judge:
    def __init__(self, market, bot_init_assets, bot_init_currencies):
        self.bot_free_assets = bot_init_assets
        self.bot_free_currencies = bot_init_currencies
        self.bot_blocked_assets = 0
        self.bot_blocked_currencies = 0

        self.market = market
        self.trades = MarketTrades.objects.order_by('time')
        self.orders = []
        self.trade_index = 0

    @property
    def no_active_order(self):
        for order in self.orders:
            if order.status == Order.OrderStatus.active:
                return False
        return True

    def incremet_trade_index(self):
        if self.trade_index < len(self.trades)-1:
            self.trade_index += 1
            return True
        return False


    def incremet_time_until_all_orders_are_matched_or_timeout(self, time_period):
        start_time = self.trades[self.trade_index].time
        while (
            self.trades[self.trade_index].time - start_time < time_period and
            self.trade_index < len(self.trades)

        ):
            for order in list(map(
                lambda o: o.is_active
            )):
                if (
                    order.price <= self.trades[self.trade_index] and
                    order.side == Order.OrderSide.sell
                ):
                    order.status = Order.OrderStatus.pending
                if (
                    order.price >= self.trades[self.trade_index] and
                    order.side == Order.OrderSide.buy
                ):
                    order.status = Order.OrderStatus.pending

            for order in list(map(
                lambda o: o.is_pending
            )):
                if order.side == Order.OrderSide.sell:
                    order.status = Order.OrderStatus.done
                    self.bot_blocked_assets -= order.amount
                    self.bot_free_currencies += (order.amount * order.price) * (1-FEE)
                if order.side == Order.OrderSide.buy:
                    order.status = Order.OrderStatus.done
                    self.bot_blocked_currencies -= (order.amount * order.price)
                    self.bot_free_assets += order.amount * (1-FEE)


    # trader queries
    def get_trade_status(self, trade_id):
        for order in self.orders:
            if order.id == trade_id:
                return order
        return None

    def place_sell_order(self, amount, price):
        if self.bot_free_assets < amount:
            False, None
        self.orders.append(
            Order(amount, price, Order.OrderSide.sell)
        )
        self.bot_free_assets -= amount
        self.bot_blocked_assets += amount
        return True, self.orders[-1].id

    def place_buy_order(self, amount, price):
        if self.bot_free_currencies < amount*price:
            False, None
        self.bot_free_currencies -= amount*price
        self.bot_blocked_currencies += amount*price
        self.orders.append(
            Order(amount, price, Order.OrderSide.buy)
        )
        return True, self.orders[-1].id

    def get_latest_trades(self, time_period):
        return list(map(
            lambda obj: obj[1],
            list(filter(
                lambda idx_trade: (
                    idx_trade[0] <= self.idx_trade and
                    idx_trade[1].time >= self.trades[self.idx_trade].time - time_period
                ),
                list(enumerate(self.trades)),
            ))
        ))
