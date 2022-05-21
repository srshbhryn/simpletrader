import time
import asyncio
import json

import tornado.ioloop
from tornado.websocket import websocket_connect, WebSocketClientConnection
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from simpletrader.base.journals import AsyncJournal
from simpletrader.kucoin.models import SpotTrade


class SpotTradeJournal(AsyncJournal):
    class Meta:
        model = SpotTrade

def restart_on_exception(func):
    async def wrapper(*args, **kwargs):
        print(f'calling {func.__name__}')
        self = args[0]
        try:
            response = await func(*args, **kwargs)
        except Exception as e:
            print(f'error in \'{func.__name__}\': {e}')
            #log exception
            await asyncio.sleep(.5)
            self.loop.add_callback(self.restart)
            raise e
        return response
    return wrapper


class BaseCollector:
    def __init__(self, loop: tornado.ioloop.IOLoop):
        self.http_client = AsyncHTTPClient()
        self.loop = loop
        self.is_ws_healthy = False
        self.symbols = ['ETH-USDT', 'BTC-USDT']
        self.journal = SpotTradeJournal()
        self.connection = None
        self.last_msg_time = None

    async def restart(self):
        try:
            self.connection.close()
            del self.connection
        except:
            pass
        await self.fetch_rest_apis()
        await self.connect_to_socket()
        await self.subscribe()
        self.loop.add_callback(self.ws_msg_callback)
        self.loop.add_callback(self.run_health_check)
        # await self.ws_msg_callback()
        # await self.run_health_check()

    async def _get_socket_url(self):
        response: HTTPResponse  = await self.http_client.fetch(HTTPRequest(
            url='https://api.kucoin.com/api/v1/bullet-public',
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
        topic = '/market/match:' + ','.join(self.symbols)
        id = (lambda ts: ts + (17 - len(ts)) * '0')(str(time.time()).replace('.', ''))
        await self.connection.write_message(json.dumps({
            'id': id,
            'topic': topic,
            'type': 'subscribe',
            'privateChannel': False,
            'response': True,
        }))
        message = await self.connection.read_message()
        print(message)
        message = json.loads(message)
        assert message.get('type') == 'ack'
        assert message.get('id') == id

    async def ws_msg_callback(self):
        self.last_msg_time = self.loop.time()
        while True:
            message = await self.connection.read_message()
            if message is None:
                raise Exception('closed connection')
            self.last_msg_time = self.loop.time()
            # self.loop.add_callback(self.journal.append_line, )
            print(message)
    # def serialize_data(self, message):
    #     return {
    #             'market_id': market_id,
    #             'time': int(trade['time'] / 10**6),
    #             'sort_field': int(trade['sequence']),
    #             'price': trade['price'],
    #             'volume': trade['size'],
    #             'is_buyer_maker': trade['side'] == 'sell',
    #         })

    # {
    #   "type":"message",
    #   topic":"/market/match:BTC-USDT",
    #   "subject":"trade.l3match",
    #   "data":{
    #       "symbol":"BTC-USDT",
    #       "side":"sell",
    #       "type":"match",
    #         "makerOrderId":"6289570819b43000013983ae","sequence":"1629863091969","size":"0.0006658","price":"29409.9","takerOrderId":"6289570e7b1b720001fe85a1","time":"1653167886422553108","tradeId":"6289570e2e113d2923dfad6b"}}

    @restart_on_exception
    async def fetch_rest_apis(self):
        pass

    async def _fetch_rest_api(self, symbol):
        pass

    @restart_on_exception
    async def run_health_check(self):
        while True:
            await asyncio.sleep(2)
            assert self.loop.time() - self.last_msg_time <= 4