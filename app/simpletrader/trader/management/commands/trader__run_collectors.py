from typing import List
import sys
import time
import multiprocessing

from django.core.management.base import BaseCommand

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.sharedconfigs import Exchange
from simpletrader.trader.models import Account
from simpletrader.trader.fill_collectors.nobitex import NobitexFillCollector



class Command(BaseCommand, GracefulKiller):
    def __init__(self, *args, **kwargs) -> None:
        self.processes: List[multiprocessing.Process] = []
        super().__init__(*args, **kwargs)
        GracefulKiller.__init__(self)

    def exit_gracefully(self, *args, **kwargs):
        for p in self.processes:
            p.terminate()
        for p in self.processes:
            p.join()
        return super().exit_gracefully(*args, **kwargs)

    def handle(self, *args, **options):
        self.collect_nobitex_fills()
        while self.is_alive:
            time.sleep(1)
        sys.exit(0)

    def collect_nobitex_fills(self):
        account_ids = Account.objects.filter(
            exchange_id=Exchange.get_by('name', 'nobitex').id
        ).values_list('id', flat=True)
        for account_id in account_ids:
            p = multiprocessing.Process(
                target=NobitexFillCollector.create_and_run,
                args=(account_id,)
            )
            self.processes.append(p)
            p.start()
