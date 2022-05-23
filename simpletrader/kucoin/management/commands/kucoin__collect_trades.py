from django.core.management.base import BaseCommand

import tornado.ioloop

from simpletrader.kucoin.wsclient import SpotTradesCollector, FuturesTradesCollector


class Command(BaseCommand):
    help = 'running asyncio loop to collect trading using kucoin websocket feed.'

    def handle(self, *args, **options):
        spot_ws = SpotTradesCollector()
        futures_ws = FuturesTradesCollector()
        tornado.ioloop.IOLoop.current().add_callback(spot_ws.restart)
        tornado.ioloop.IOLoop.current().add_callback(futures_ws.restart)
        tornado.ioloop.IOLoop.current().start()
