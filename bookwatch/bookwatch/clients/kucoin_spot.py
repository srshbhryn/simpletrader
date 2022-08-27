import time
import asyncio
import json

import tornado.ioloop
from tornado.websocket import websocket_connect, WebSocketClientConnection
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from bookwatch.markets import kucoin_spot_markets
from bookwatch.clients.redis import redis
from bookwatch.clients.utils import restart_on_exception

class BaseKucoin:
    base_url = None

    def __init__(self):
        self.http_client = AsyncHTTPClient()
        self.loop = tornado.ioloop.IOLoop.current()
        self.is_ws_healthy = False
        self.connection = None
        self.last_msg_time = None
        self.symbol_to_id_map = {
            m.symbol: m.id
            for m in kucoin_spot_markets
        }
        self.topic = ','.join([m.symbol for m in kucoin_spot_markets])

    async def restart(self):
        await asyncio.sleep(.1)
        try:
            self.connection.close()
            del self.connection
        except:
            pass
        await self.connect_to_socket()
        await self.subscribe()
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
            'topic': '/market/ticker:' + self.topic,
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
                raise Exception('connection closed ')
            self.last_msg_time = self.loop.time()
            message = json.loads(message)
            symbol = message['topic'].split(':')[1]
            data = message['data']
            data = ','.join([
                    str(data['time']),
                    data['bestAsk'],
                    data['bestAskSize'],
                    data['bestBid'],
                    data['bestBidSize'],
                ])

            self.loop.add_callback(
                redis.set,
                name=self.symbol_to_id_map[symbol],
                value=data,
            )

    @restart_on_exception
    async def run_health_check(self):
        while True:
            await asyncio.sleep(2)
            assert self.loop.time() - self.last_msg_time <= 2


class KucoinSpot(BaseKucoin):
    base_url = 'https://api.kucoin.com'
