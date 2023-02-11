import json
from asyncio import sleep

import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from bookwatch.config import Market, Exchange, MarketType, Asset
from bookwatch.clients.redis import redis


class Nobitex:
    def __init__(self) -> None:
        self.client = AsyncHTTPClient()
        self.nobitex_markets = [
            market for market in Market
            if market.value.exchange == Exchange.Nobitex
        ]
        self.loop: tornado.ioloop.IOLoop = tornado.ioloop.IOLoop.current()

    def get_symbol(self, market: MarketType):
        market = market.value
        base = market.pair.value.base_asset.name
        if market.pair.value.quote_asset == Asset.RLS:
            quote = 'IRT'
        else:
            quote = market.pair.value.quote_asset.name
        return base + quote

    async def run(self):
        while True:
            self.loop.add_callback(self.fetch_and_store)
            await sleep(2)

    async def fetch_and_store(self):
        try:
            response: HTTPResponse  = await AsyncHTTPClient().fetch(request=HTTPRequest(
                url='https://api.nobitex.ir/v2/orderbook/all',
                method='GET',
                body=None,
                connect_timeout=2,
                request_timeout=2,
            ), raise_error=False)
            body: dict = json.loads(response.body)
            assert body['status'] == 'ok'
            for market in self.nobitex_markets:
                symbol = self.get_symbol(market)
                data = [str(body[symbol]['lastUpdate'])]
                data += body[symbol]['bids'][0]
                data += body[symbol]['asks'][0]
                data = ','.join(data)
                await redis.set(name=market.value.id, value=data)
        except Exception as e:
            print(f'ERROR: {e}')
