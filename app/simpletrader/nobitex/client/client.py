import random
import requests
import json

# from .helpers import interval_to_milliseconds, convert_ts_str
# from .exceptions import BinanceAPIException, BinanceRequestException, NotImplementedException
# from .enums import HistoricalKlinesType


class BaseClient:

    API_URL = 'https://api.nobitex.ir/v2'

    def __init__(self, token=None):
        self.token = token
        self._init_session()

    def _init_session(self):
        self.public_session = requests.Session()
        self.public_session.headers = self._public_headers
        if self.token is not None:
            self.private_session = requests.Session()
            self.private_session.headers = {
                **self._public_headers,
                'Authorization': f'Token {self.token}',

            }
        else:
            self.private_session = None

    @property
    def _public_headers(self):
        return {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }


class MarketDataMixIn:
    def get_orderbook(self, symbol):
        response  = self.public_session.get(self.API_URL+f'/orderbook/{symbol}')
        response_json = json.loads(response.text)
        return {
            'bids': [
                {
                    'price': float(bid[0]),
                    'volume': float(bid[1]),
                }
                for bid in response_json['bids']
            ],
            'asks': [
                {
                    'price': float(ask[0]),
                    'volume': float(ask[1]),
                }
                for ask in response_json['asks']
            ]
        }

    def get_trades(self, symbol):
        '''
            limit 15 req/m
            no token required
        '''
        response  = self.public_session.get(self.API_URL+f'/trades/{symbol}')
        response_json = json.loads(response.text)
        return {
            'trades': [
                {
                    'time': trade['time'],
                    'price': float(trade['price']),
                    'volume': float(trade['volume']),
                    'is_buy': trade['type']=='buy'
                }
                for trade in response_json['trades']
            ]
        }


class Client(
        BaseClient,
        MarketDataMixIn,
    ):
        pass

clients = [
    Client()
    for _ in range(100)
]

def get_client():
    return clients[random.randrange(100)]
    # return random.choice(clients)
