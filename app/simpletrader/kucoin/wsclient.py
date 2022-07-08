import time
import asyncio
import json
import logging

import tornado.ioloop
from tornado.websocket import websocket_connect, WebSocketClientConnection
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from simpletrader.base.models import Exchange
from simpletrader.base.journals import AsyncJournal
from simpletrader.kucoin.models import SpotMarket, FuturesContract, Trade, Market

logger = logging.getLogger('django')

class TradeJournal(AsyncJournal):
    class Meta:
        model = Trade


def restart_on_exception(func):
    async def wrapper(*args, **kwargs):
        logger.info(f'restart_on_exception: calling {func.__name__}')
        self = args[0]
        try:
            response = await func(*args, **kwargs)
        except Exception as e:
            logger.warning(f'restart_on_exception: error in \'{func.__name__}\': {e}')
            await asyncio.sleep(.5)
            self.loop.add_callback(self.restart)
            raise e
        return response
    return wrapper


class BaseCollector:

    def __init__(self):
        self.http_client = AsyncHTTPClient()
        self.loop = tornado.ioloop.IOLoop.current()
        self.is_ws_healthy = False
        self.connection = None
        self.last_msg_time = None
        self.initialize()
        assert self.symbol_to_market_id_map is not None
        assert self.journal is not None
        assert self.base_url is not None
        assert self.fetch_api_path_template is not None
        self.fetch_api_url_template = self.base_url + self.fetch_api_path_template

    def initialize(self):
        raise NotImplementedError

    async def restart(self):
        await asyncio.sleep(.1)
        try:
            self.connection.close()
            del self.connection
        except:
            pass
        self.loop.add_callback(self.fetch_rest_apis)
        await self.connect_to_socket()
        await self.subscribe()
        logger.info('connected to ws')
        self.loop.add_callback(self.ws_msg_callback)
        self.loop.add_callback(self.run_health_check)

    async def _get_socket_url(self):
        response: HTTPResponse  = await self.http_client.fetch(HTTPRequest(
            # url=f'{self.base_url}/api/v1/bullet-public',
            url=f'{self.base_url}/api/v1/bullet-public',
            method='POST',
            body=None,
            allow_nonstandard_methods=True,
        ))
        data = json.loads(response.body)['data']
        token = data['token']
        ws_url = data['instanceServers'][0]['endpoint']
        return f'{ws_url}?token={token}'

    @restart_on_exception
    async def connect_to_socket(self):
        ws_url = await self._get_socket_url()
        self.connection: WebSocketClientConnection = await websocket_connect(
            url=ws_url,
        )
        message = await self.connection.read_message()
        message = json.loads(message)
        assert message.get('type') == 'welcome'

    @restart_on_exception
    async def subscribe(self):
        id = (lambda ts: ts + (17 - len(ts)) * '0')(str(time.time()).replace('.', ''))
        await self.connection.write_message(json.dumps({
            'id': id,
            'topic': self.topic,
            'type': 'subscribe',
            'privateChannel': False,
            'response': True,
        }))
        message = await self.connection.read_message()
        message = json.loads(message)
        assert message.get('type') == 'ack'
        assert message.get('id') == id

    async def ws_msg_callback(self):
        self.last_msg_time = self.loop.time()
        while True:
            message = await self.connection.read_message()
            if message is None:
                raise Exception('closed connection')
            logger.debug(message)
            self.last_msg_time = self.loop.time()
            message = json.loads(message)
            self.loop.add_callback(self.journal.append_line, self.serialize_data(message['data']))

    def serialize_data(self, data):
        raise NotImplementedError

    async def fetch_rest_apis(self):
        for symbol in self.symbol_to_market_id_map:
            self.loop.add_callback(self._fetch_rest_api, symbol)

    async def _fetch_rest_api(self, symbol):
        response: HTTPResponse  = await self.http_client.fetch(HTTPRequest(
            url=self.fetch_api_url_template.format(symbol),
            method='GET',
            body=None,
        ))
        trades = json.loads(response.body).get('data')
        for trade in trades:
            trade['symbol'] = symbol
            self.loop.add_callback(self.journal.append_line, self.serialize_data(trade))

    @restart_on_exception
    async def run_health_check(self):
        while True:
            await asyncio.sleep(8)
            assert self.loop.time() - self.last_msg_time <= 4


class SpotTradesCollector(BaseCollector):
    def initialize(self):
        self.journal = TradeJournal()
        spot_markets = SpotMarket.objects.all()
        symbols = [market.symbol for market in spot_markets]
        self.topic = f'/market/match:{",".join(symbols)}'
        markets = Market.objects.filter(type=Exchange.kucoin_spot).values_list('id', 'related_id')
        self.symbol_to_market_id_map = {
            market.symbol: next(
                (mr[0] for mr in markets if mr[1] == market.id)
            )
            for market in spot_markets
        }
        self.base_url = 'https://api.kucoin.com'
        self.fetch_api_path_template = '/api/v1/market/histories?symbol={}'

    def serialize_data(self, data):
        return {
            'market_id': self.symbol_to_market_id_map[data['symbol']],
            'time': int(int(data['time']) / 10**6),
            'sort_field': int(data['sequence']),
            'price': data['price'],
            'volume': data['size'],
            'is_buyer_maker': data['side'] == 'sell',
        }


class FuturesTradesCollector(BaseCollector):
    def initialize(self):
        self.journal = TradeJournal()
        futures_markets = FuturesContract.objects.all()
        symbols = [futures_market.symbol for futures_market in futures_markets]
        self.topic = f'/contractMarket/execution:{",".join(symbols)}'
        markets = Market.objects.filter(type=Exchange.kucoin_futures).values_list('id', 'related_id')
        self.symbol_to_market_id_map = {
            market.symbol: next(
                (mr[0] for mr in markets if mr[1] == market.id)
            )
            for market in futures_markets
        }
        self.base_url = 'https://api-futures.kucoin.com'
        self.fetch_api_path_template = '/api/v1/trade/history?symbol={}'

    def serialize_data(self, data):
        return {
            'market_id': self.symbol_to_market_id_map[data['symbol']],
            'time': int(int(data['ts']) / 10**6),
            'sort_field': int(data['sequence']),
            'price': data['price'],
            'volume': data['size'],
            'is_buyer_maker': data['side'] == 'sell',
        }
