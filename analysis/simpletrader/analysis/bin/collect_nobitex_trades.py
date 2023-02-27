import os
import logging
import asyncio
import json

import django
import sentry_sdk

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpletrader.settings')
django.setup()


from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPResponse
from tornado import ioloop

from simpletrader.analysis.journals import AsyncTradeJournal
from simpletrader.analysis.models import Market, Exchange, Asset
from simpletrader.base.utils import GracefulKiller


log = logging.getLogger('django')


class NobitexTradeCollector(GracefulKiller):

    def __init__(self):
        super().__init__()
        nobitex_exchange_id = Exchange.objects.get(name='nobitex').id
        assets = dict(list(Asset.objects.values_list('id', 'name')))
        assets[2] = 'irt'
        markets = Market.objects.filter(exchange_id=nobitex_exchange_id)
        self.shib_market_ids = list(markets.filter(pair__base_asset=Asset.objects.get(name='shib')).values_list('id', flat=True))
        self.market_id_to_symbol_map = {}
        self.symbol_to_market_id_map = {}
        for market in markets:
            symbol = (assets[market.base_asset.id] + assets[market.quote_asset.id]).upper()
            self.market_id_to_symbol_map[market.id] = symbol
            self.symbol_to_market_id_map[symbol] = market.id
        self.client = AsyncHTTPClient()
        self.requests = {
            market_id: HTTPRequest(f'https://api.nobitex.ir/v2/trades/{symbol}')
            for market_id, symbol in self.market_id_to_symbol_map.items()
        }
        self.journal = AsyncTradeJournal()

    async def run(self):
        while self.is_alive:
            try:
                for market_id in self.market_id_to_symbol_map:
                    ioloop.IOLoop.current().add_callback(self.fetch_market, market_id=market_id)
            except:
                sentry_sdk.capture_exception()
            await asyncio.sleep(3)

    async def fetch_market(self, market_id,):
        response: HTTPResponse = await self.client.fetch(self.requests[market_id])
        for trade in json.loads(response.body)['trades']:
            await self.journal.append_line(self._serialize_trade(trade, market_id))

    def _serialize_trade(self, obj, market_id):
        price_parts = str(obj['price']).split('.')
        is_buyer_maker = obj['type'] == 'sell'
        if len(price_parts) == 1:
            price_parts += ['0']
        if len(price_parts[0]) < 10:
            price_parts[0] = price_parts[0] + (10 - len(price_parts[0])) * '0'
        if len(price_parts[1]) < 10:
            price_parts[1] = (10 - len(price_parts[1])) * '0' + price_parts[1]
        sort_field = str(obj['time']) + (
            '0' if is_buyer_maker else '1'
        ) + price_parts[1] + price_parts[0]
        price = float(obj['price'])
        volume = float(obj['volume'])
        base_amount = volume
        if market_id in self.shib_market_ids:
            base_amount *= 1000
        quote_amount = volume * price
        return({
            'market_id': market_id,
            'time': obj['time'],
            'sort_field': sort_field,
            'base_amount': base_amount,
            'quote_amount': quote_amount,
            'is_buyer_maker': is_buyer_maker,
        })


def main():
    collector = NobitexTradeCollector()
    asyncio.run(collector.run())


if __name__ in ('__main__', 'django.core.management.commands.shell',):
    main()
