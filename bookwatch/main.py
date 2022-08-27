import logging

import tornado.ioloop

from bookwatch.clients.nobitex import Nobitex

if __name__ == '__main__':
    logger = logging.getLogger()
    nobitex = Nobitex()
    logger.info('start')
    tornado.ioloop.IOLoop.current().add_callback(nobitex.run)
    tornado.ioloop.IOLoop.current().start()