from django.core.management.base import BaseCommand

import tornado.ioloop

from simpletrader.kucoin.wsclient import SpotTradesCollector


class Command(BaseCommand):
    help = 'running asyncio loop to collect trading using kucoin websocket feed.'

    def handle(self, *args, **options):
        ws = SpotTradesCollector()
        tornado.ioloop.IOLoop.current().add_callback(ws.restart)
        tornado.ioloop.IOLoop.current().start()