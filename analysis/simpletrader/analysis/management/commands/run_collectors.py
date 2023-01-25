from typing import List
import sys
import time
import multiprocessing

from django.core.management.base import BaseCommand

from simpletrader.base.utils import GracefulKiller
from simpletrader.analysis.bin import store_trades
from simpletrader.analysis.bin import collect_nobitex_trades


multiprocessing.set_start_method('spawn')


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
        self.run_db_inserter()
        self.run_nobitex_collector()
        while self.is_alive:
            time.sleep(1)
        sys.exit(0)

    def run_db_inserter(self):
        p = multiprocessing.Process(
            target=store_trades.main,
            args=(),
        )
        self.processes.append(p)
        p.start()


    def run_nobitex_collector(self):
        p = multiprocessing.Process(
            target=collect_nobitex_trades.main,
            args=(),
        )
        self.processes.append(p)
        p.start()
