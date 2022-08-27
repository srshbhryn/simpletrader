import logging

import tornado.ioloop

from bookwatch.clients.nobitex import Nobitex
from bookwatch.clients.kucoin_spot import KucoinSpot

if __name__ == '__main__':
    logger = logging.getLogger()
    nobitex = Nobitex()
    kucoin_spot = KucoinSpot()
    tornado.ioloop.IOLoop.current().add_callback(nobitex.run)
    kucoin_spot = tornado.ioloop.IOLoop.current().add_callback(kucoin_spot.restart)
    tornado.ioloop.IOLoop.current().start()