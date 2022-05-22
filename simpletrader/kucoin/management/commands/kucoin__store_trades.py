import time

from django.core.management.base import BaseCommand

from simpletrader.kucoin.journals import SpotTradeJournal, FuturesTradeJournal


class Command(BaseCommand):
    help = 'read journals and store trades in database'

    def handle(self, *args, **options):
        spot_journal = SpotTradeJournal()
        futures_journal = FuturesTradeJournal()
        while True:
            time.sleep(.5)
            spot_journal.insert_to_db()
            futures_journal.insert_to_db()