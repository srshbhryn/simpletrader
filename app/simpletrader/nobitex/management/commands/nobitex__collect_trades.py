import logging

from django.core.management.base import BaseCommand

from simpletrader.nobitex.collect_trades import TradeCollector

logger = logging.getLogger('django')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tc = TradeCollector()
        tc._initialize()
        while True:
            try:
                tc.run()
            except KeyboardInterrupt:
                return
            except Exception as e:
                logger.error(e)
