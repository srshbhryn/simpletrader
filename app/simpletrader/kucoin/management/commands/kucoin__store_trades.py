import time

from django.core.management.base import BaseCommand

from simpletrader.kucoin.journals import SpotTradeJournal, FuturesTradeJournal, TradeJournal


class Command(BaseCommand):
    help = 'read journals and store trades in database'

    def handle(self, *args, **options):
        # spot_journal = SpotTradeJournal()
        # futures_journal = FuturesTradeJournal()
        jounral = TradeJournal()
        while True:
            time.sleep(.4)
            jounral.insert_to_db()
            # spot_journal
            # futures_journal.insert_to_db()