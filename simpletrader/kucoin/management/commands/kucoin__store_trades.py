import time

from django.core.management.base import BaseCommand


from simpletrader.kucoin.journals import SpotTradeJournal


class Command(BaseCommand):
    help = '######################'

    def handle(self, *args, **options):
        journal = SpotTradeJournal()
        while True:
            time.sleep(.4)
            lines = journal._read_lines()
            # if len(lines):
            if True:
                print(f'fetched {len(lines)} trades')
            # for l in lines:
            #     print(l)