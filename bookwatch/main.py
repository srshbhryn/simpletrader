import tornado.ioloop

from bookwatch.clients.nobitex import Nobitex
from bookwatch.clients.kucoin import KucoinSpot, KucoinFutures

if __name__ == '__main__':
    tornado.ioloop.IOLoop.current().add_callback(Nobitex().run)
    tornado.ioloop.IOLoop.current().add_callback(KucoinSpot().restart)
    tornado.ioloop.IOLoop.current().add_callback(KucoinFutures().restart)
    tornado.ioloop.IOLoop.current().start()
