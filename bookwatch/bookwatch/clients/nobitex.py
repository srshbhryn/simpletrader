import json
from asyncio import sleep

import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from bookwatch.markets import nobitex_markets
from bookwatch.clients.redis import redis

class Nobitex:
    def __init__(self) -> None:
        self.client = AsyncHTTPClient()
        self.loop: tornado.ioloop.IOLoop = tornado.ioloop.IOLoop.current()

    async def run(self):
        while True:
            self.loop.add_callback(self.fetch_and_store)
            await sleep(2)

    async def fetch_and_store(self):
        try:
            response: HTTPResponse  = await AsyncHTTPClient().fetch(request=HTTPRequest(
                url='http://api.nobitex.ir/v2/orderbook/all',
                method='GET',
                body=None,
                connect_timeout=2,
                request_timeout=2,
            ), raise_error=False)
            body: dict = json.loads(response.body)
            assert body['status'] == 'ok'
            for market in nobitex_markets:
                symbol = market.symbol
                data = [str(body[symbol]['lastUpdate'])]
                data += body[symbol]['bids'][0]
                data += body[symbol]['asks'][0]
                data = ','.join(data)
                self.loop.add_callback(redis.set, name=market.id, value=data)
        except Exception as e:
            print(e)
