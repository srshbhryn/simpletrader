
import time
from datetime import timedelta
import threading

from typing import List

from django.core.cache import cache
from django.db import transaction, models
from django.utils.timezone import now
import sentry_sdk

from simpletrader.base.utils import float_to_decimal, ReadWriteLock, GracefulKiller
from simpletrader.analysis.models import OrderStatus, Exchange, Pair, Market, Trade
from simpletrader.accounts.models import Account, Transaction
from simpletrader.trade.models import Order, Fill


RELOAD_ACCOUNTS_CACHE_KEY = 'reload_nobitex_accounts'


class NobitexDemoMatcher(GracefulKiller):
    def __init__(self) -> None:
        self.sleep_time: timedelta = timedelta(seconds=2)
        self.account_ids: List[int] = []
        self.nobitex: Exchange = None
        self.pairs: List[Pair] = []
        self.reload_accounts_cache_key = RELOAD_ACCOUNTS_CACHE_KEY
        self.fee_factor = float_to_decimal(1 - 0.001)
        self.pair_id_to_market_id_map: dict = None
        self.failed_order_status_id: int = None
        self.filled_order_status_id: int = None
        self.open_order_status_id: int = None
        self.canceled_order_status_id: int = None
        self.mutex: ReadWriteLock = None
        GracefulKiller.__init__(self)

    def run(self) -> None:
        self.nobitex = Exchange.objects.get(name='nobitex')
        self.pair_id_to_market_id_map = dict(list(Market.objects.filter(
            exchange=self.nobitex
        ).values_list('pair_id', 'id',)))
        self.pairs = Pair.objects.filter(id__in=list(self.pair_id_to_market_id_map.keys()))
        self.failed_order_status_id: int = OrderStatus.objects.get(name='failed').id
        self.filled_order_status_id: int = OrderStatus.objects.get(name='filled').id
        self.open_order_status_id: int = OrderStatus.objects.get(name='open').id
        self.canceled_order_status_id: int = OrderStatus.objects.get(name='canceled').id
        self.mutex = ReadWriteLock()
        self.fetch_accounts()
        for pair in self.pairs:
            thread = threading.Thread(target=self.run_for_pair, args=(pair,))
            thread.daemon = True
            thread.start()

        while self.is_alive:
            time.sleep(self.sleep_time.total_seconds())
            if cache.get(self.reload_accounts_cache_key):
                self.mutex.acquire_write()
                try:
                    self.reload_accounts()
                    cache.decr(self.reload_accounts_cache_key)
                except:
                    sentry_sdk.capture_exception()
                finally:
                    self.mutex.release_write()

    def reload_accounts(self):
        self.accounts = Account.objects.filter(type=Account.Types.demo, exchange=self.nobitex)

    def fetch_accounts(self):
        cache.set(self.reload_accounts_cache_key, 0)
        self.accounts = Account.objects.filter(type=Account.Types.demo, exchange=self.nobitex)

    def fetch_orders(self, pair: Pair, max_price: float, min_price: float) -> List[Order]:
        return list(Order.objects.select_for_update().filter(
            account__type=Account.Types.demo,
            account__exchange=self.nobitex,
            status_id=self.open_order_status_id,
            pair=pair,
            exchange=self.nobitex,
        ))

    def get_price_minmax(self, pair: Pair) -> tuple[float, float]:
        nw = now()
        min_max = Trade.objects.filter(
            market_id=self.pair_id_to_market_id_map[pair.id],
            time__gt=nw - timedelta(minutes=1),
            time__lt=nw,
        ).aggregate(
            min_price=models.Min(models.F('quote_amount') / models.F('base_amount')),
            max_price=models.Max(models.F('quote_amount') / models.F('base_amount')),
        )
        return min_max.get('min_price'), min_max.get('max_price')

    def run_for_pair(self, pair: Pair):
        while True:
            try:
                time.sleep(self.sleep_time.total_seconds())
                self.mutex.acquire_read()
                min_price, max_price = self.get_price_minmax(pair,)
                if min_price is None:
                    self.mutex.release_read()
                    time.sleep(1)
                    continue
                self.do_all_orders(pair, min_price, max_price,)
            except:
                sentry_sdk.capture_exception()
            self.mutex.release_read()

    @transaction.atomic
    def do_order(self, order: Order, min_price: float, max_price: float,):
        min_price = float_to_decimal(min_price)
        max_price = float_to_decimal(max_price)
        if order.is_sell and order.price > max_price:
            return

        if not order.is_sell and order.price < min_price:
            return

        if order.price >= min_price and order.price <= max_price:
            execution_price = order.price

        elif order.is_sell and order.price < min_price:
            execution_price = min_price

        elif not order.is_sell and order.price > max_price:
            execution_price = max_price

        blocked_asset = order.pair.base_asset if order.is_sell else order.pair.quote_asset
        blocked_amount = order.volume * (float_to_decimal(1) if order.is_sell else order.price)


        asset_to_get = order.pair.quote_asset if order.is_sell else order.pair.base_asset
        amount_to_get = (execution_price * order.volume if order.is_sell else order.volume) * self.fee_factor

        asset_to_give = blocked_asset
        amount_to_give = order.volume if order.is_sell else execution_price * order.volume

        fee_asset = asset_to_get
        fee_amount = (execution_price * order.volume if order.is_sell else order.volume) * (1 - self.fee_factor)

        execution_price = float_to_decimal(execution_price)

        asset_to_get_wallet = order.account.get_wallet(asset_to_get.id)
        asset_to_give_wallet = order.account.get_wallet(asset_to_give.id)

        transactions = []
        transactions.append(
            (
                (asset_to_give_wallet.id, Transaction.Type.add_to_blocked_balance),
                lambda : asset_to_give_wallet.create_transaction(
                    type=Transaction.Type.add_to_blocked_balance,
                    amount=-float_to_decimal(amount_to_give),
                ),
            )
        )
        transactions.append(
            (
                (asset_to_give_wallet.id, Transaction.Type.block),
                lambda : asset_to_give_wallet.create_transaction(
                    type=Transaction.Type.block,
                    amount=-float_to_decimal(blocked_amount - amount_to_give),
                ),
            )
        )
        transactions.append(
            (
                (asset_to_get_wallet.id, Transaction.Type.subtract_from_free_balance),
                lambda : asset_to_get_wallet.create_transaction(
                    type=Transaction.Type.subtract_from_free_balance,
                    amount=-float_to_decimal(amount_to_get),
                ),
            )
        )
        transactions = sorted(transactions, key=lambda ent: 10 * ent[0][0] + ent[0][1])

        for _, fun in transactions:
            fun()

        Order.objects.filter(uid=order.uid).update(status_id=self.filled_order_status_id)
        Fill.objects.create(
            account=order.account,
            order_uid=order.uid,
            external_id=order.uid.hex,
            external_order_id=order.uid.hex,
            pair=order.pair,
            exchange=self.nobitex,
            price=float_to_decimal(execution_price),
            volume=order.volume,
            is_sell=order.is_sell,
            fee=float_to_decimal(fee_amount),
            fee_asset=fee_asset,
        )

    @transaction.atomic
    def do_all_orders(self, pair: Pair, min_price: float, max_price: float,) -> None:
        for order in self.fetch_orders(pair, min_price, max_price,):
            self.do_order(order, min_price, max_price,)
