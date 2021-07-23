
from typing import Dict, Optional, List, Tuple

import requests
import json

# from .helpers import interval_to_milliseconds, convert_ts_str
# from .exceptions import BinanceAPIException, BinanceRequestException, NotImplementedException
# from .enums import HistoricalKlinesType


class BaseClient:

    API_URL = 'https://api.nobitex.ir/v2'

    def __init__(self):
        self._init_session()

    def _init_session(self):
        self.session = requests.Session()

    def _init_headers(self) -> Dict:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',  # noqa
        }
        # if self.API_KEY:
        #     assert self.API_KEY
        #     headers['X-MBX-APIKEY'] = self.API_KEY
        return headers


    # def _create_api_uri(self, path: str, signed: bool = True, version: str = PUBLIC_API_VERSION) -> str:
    #     url = self.API_URL
    #     if self.testnet:
    #         url = self.API_TESTNET_URL
    #     v = self.PRIVATE_API_VERSION if signed else version
    #     return url + '/' + v + '/' + path

class MarketDataMixIn:
    def get_orderbook(self, symbol):
        response  = self.session.get(self.API_URL+f'/orderbook/{symbol}')
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
        response  = self.session.get(self.API_URL+f'/trades/{symbol}')
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
