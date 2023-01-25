import os
import time
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpletrader.settings')
django.setup()

from simpletrader.analysis.journals import TradeJournal
from simpletrader.base.utils import GracefulKiller


log = logging.getLogger('django')


class StoreTrades(GracefulKiller):

    def __init__(self) -> None:
        super().__init__()
        self.jounral = TradeJournal()

    def run(self):
        while self.is_alive:
            try:
                self.jounral.insert_to_db()
            except Exception as e:
                log.error(e)
            time.sleep(.1)


def main():
    store = StoreTrades()
    store.run()


if __name__ in ('__main__', 'django.core.management.commands.shell',):
    main()
