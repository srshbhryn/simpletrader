from django.core.management.base import BaseCommand

import tornado.ioloop

from simpletrader.kucoin.wsclient import BaseCollector
from simpletrader.kucoin.models import SpotMarket, FuturesContract

class Command(BaseCommand):
    help = 'running asyncio loop to collect trading using kucoin websocket feed.'

    def handle(self, *args, **options):
        symbol_to_market_id_map = {
            market.symbol: market.id
            for market in SpotMarket.objects.all()
        }
        ws = BaseCollector(tornado.ioloop.IOLoop.current(), symbol_to_market_id_map)
        tornado.ioloop.IOLoop.current().add_callback(ws.restart)
        tornado.ioloop.IOLoop.current().start()