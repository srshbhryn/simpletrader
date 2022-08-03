import logging
from datetime import datetime

from django.core.management.base import BaseCommand

from simpletrader.nobitex.collect_trades import TradeCollector

logger = logging.getLogger('django')

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print(f'START\t{datetime.now()}')
        tc = TradeCollector()
        tc._initialize()
        while True:
            try:
                tc.run()
            except KeyboardInterrupt:
                return