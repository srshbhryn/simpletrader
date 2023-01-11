from typing import List
import sys
import time
import multiprocessing

from django.core.management.base import BaseCommand

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.sharedconfigs import Exchange
from simpletrader.trader.models import Account
from simpletrader.trader.fill_collectors import NobitexFillCollector, KucoinFuturesFillCollector
from simpletrader.trader.balance_collectors import NobitexBalanceCollector, KucoinFuturesBalanceCollector
from simpletrader.trader.clients.book_watch import get_best_price


# multiprocessing.set_start_method('spawn')


class Command(BaseCommand, GracefulKiller):
    def __init__(self, *args, **kwargs) -> None:

        self.processes: List[multiprocessing.Process] = []
        super().__init__(*args, **kwargs)
        GracefulKiller.__init__(self)

