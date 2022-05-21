from django.core.management.base import BaseCommand
from django.conf import settings

import tornado.ioloop

from simpletrader.kucoin.wsclient import BaseCollector


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Tornado says hello!")


class Command(BaseCommand):
    help = '######################'

    def handle(self, *args, **options):
        ws = BaseCollector(tornado.ioloop.IOLoop.current())
        tornado.ioloop.IOLoop.current().add_callback(ws.restart)
        tornado.ioloop.IOLoop.current().start()