
import time
from datetime import datetime, timedelta
import multiprocessing

from typing import List

from django.core.cache import cache
from django.db import transaction, models

from simpletrader.analysis.models import Asset, OrderStatus, Exchange, Pair, Market
from simpletrader.accounts.models import Account
from simpletrader.trade.models import Order, Fill


multiprocessing.set_start_method('spawn')


class NobitexDemoMatcher:
    def __init__(self) -> None:
        self.sleep_time: timedelta = timedelta(seconds=2)
        self.account_ids: List[int] = []
        self.nobitex: Exchange = None
        self.pairs: List[Pair] = []
        self.open_order_state = OrderStatus.objects.get(name='open').id
        self.reload_accounts_cache_key = 'reload_nobitex_accounts'

    def _init(self) -> None:
        self.nobitex = Exchange.objects.get(name='nobitex')
        self.pairs = list()

    def reload_account(self):
        pass

    def fetch_accounts(self):
        cache.set(self.reload_accounts_cache_key, 0)
        self.accounts = Account.objects.filter(type=Account.Types.demo, exchange=self.nobitex)

    def fetch_orders(self, pair: Pair, max_price: float, min_price: float) -> List[Order]:
        return list(Order.objects.select_for_update().filter(
            account__type=Account.Types.demo,
            account__exchange=self.nobitex,
            pair=pair,
            exchange=self.nobitex,
        ).filter(
        ))

    def get_price_minmax(self, pair: Pair) -> tuple[float, float]:
        pass

    def run_for_pair(self, pair: Pair):
        while True:
            try:
                time.sleep(self.sleep_time.total_seconds())
                min_price, max_price = self.get_price_minmax(pair,)
                self.do_all_orders(pair, min_price, max_price,)
            except Exception as e:
                print(f'ERROR{e}')

    @transaction.atomic
    def do_order(self, order: Order):
        #mareket vs limit

    @transaction.atomic
    def do_all_orders(self, pair: Pair, min_price: float, max_price: float,) -> None:
        for order in self.fetch_orders(pair, min_price, max_price,):
            self.do_order(order)
