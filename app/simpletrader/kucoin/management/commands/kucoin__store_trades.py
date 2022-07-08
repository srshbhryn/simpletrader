import time

from django.core.management.base import BaseCommand

from simpletrader.kucoin.journals import TradeJournal


class Command(BaseCommand):
    help = 'read journals and store trades in database'

    def handle(self, *args, **options):
        jounral = TradeJournal()
        while True:
            time.sleep(.2)
            jounral.insert_to_db()
