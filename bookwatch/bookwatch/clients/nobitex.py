import json
from asyncio import sleep

import tornado.ioloop
from tornado import httpserver
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from bookwatch.markets import nobitex_markets
from bookwatch.clients.redis import redis

class Nobitex:
    request = HTTPRequest(
        url='http://api.nobitex.ir/v2/orderbook/all',
        method='GET',
        body=None,
    )
    def __init__(self) -> None:
        self.client = AsyncHTTPClient()
        self.loop: tornado.ioloop.IOLoop = tornado.ioloop.IOLoop.current()

    async def run(self):
        while True:
            start_time = self.loop.time()
            try:
                response: HTTPResponse  = await self.client.fetch(self.request)
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
            sleep_time = 1.05 - (
                self.loop.time() - start_time
            )
            if sleep_time <= 0:
                continue
            await sleep(sleep_time)

