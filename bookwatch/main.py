import logging

import tornado.ioloop

from bookwatch.clients.nobitex import Nobitex
from bookwatch.clients.kucoin import KucoinSpot, KucoinFutures

if __name__ == '__main__':
    logger = logging.getLogger()
    nobitex = Nobitex()
    kucoin_spot = KucoinSpot()
    kucoin_futures = KucoinFutures()
    tornado.ioloop.IOLoop.current().add_callback(nobitex.run)
    # tornado.ioloop.IOLoop.current().add_callback(kucoin_spot.restart)
    tornado.ioloop.IOLoop.current().add_callback(kucoin_futures.restart)
    tornado.ioloop.IOLoop.current().start()