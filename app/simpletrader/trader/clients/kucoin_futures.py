from typing import TypedDict, Dict

import base64
import hmac
import hashlib
import requests
import logging
import time


from simpletrader.base.utils import LimitGuard
from simpletrader.trader.sharedconfigs import Asset, Market
from .base import OrderParams, ExchangeClientError, BaseClient


logger = logging.getLogger('django')


class KucoinFuturesError(ExchangeClientError):
    pass

class Serializer:
    # @classmethod
    # def serialize_fill(self, fill: dict) -> dict:
    #     market: Market = Market.get_by('symbol', fill['market'])
    #     is_sell = fill['type'] == 'sell'
    #     fee_asset_id = market.quote_asset.id if is_sell else market.base_asset.id
    #     return {
    #         'exchange_id': fill['id'],
    #         'exchange_order_id': fill['orderId'],
    #         'market_id': market.id,
    #         'timestamp': datetime.fromisoformat(fill['timestamp']),
    #         'is_sell': is_sell,
    #         'price': Decimal(fill['price']),
    #         'volume': Decimal(fill['price']),
    #         'fee': Decimal(fill['fee']),
    #         'fee_asset_id': fee_asset_id
    #     }

    @classmethod
    def serialize_order(self, order: dict) -> OrderParams:
        pass

    @classmethod
    def deserialize_order(self, order: OrderParams) -> dict:
        pass


def handle_exception(func):
    def wrapper(*args, **kwargs):
        self: KucoinFutures = args[0]
        while True:
            try:
                response = func(*args, **kwargs)
            # except requests.RequestException as e:
            #     if e.response and e.response.status_code == 403:
            #         self.initialize()
            #         continue
            #     elif e.response and e.response.status_code == 400:
            #         logger.info(e)
            #         return None
            except Exception as e:
                logger.error(e)
                time.sleep(10)
            return response
    return wrapper


class KucoinFutures(BaseClient):
    base_url = 'https://api-futures.kucoin.com'
    def __init__(self, credentials: dict, token: str):
        self.bot_token  = token
        self.api_key = credentials['api_key']
        self.api_secret = credentials['api_secret']
        self.api_passphrase = credentials['api_passphrase']
        self.headers: Dict[int, Dict] = {
            KucoinFutures.TYPE.public: {},
            KucoinFutures.TYPE.private: {},
        }
        self.headers[KucoinFutures.TYPE.public] = {
            'content-type': 'application/json',
        }
        passphrase = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.api_passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        )
        self.headers[KucoinFutures.TYPE.private] = {
            **self.headers[KucoinFutures.TYPE.public],
            'KC-API-KEY': self.api_key,
            'KC-API-KEY-VERSION': '2',
            'KC-API-PASSPHRASE': passphrase,
        }

    def _signed_headers(self, path: str, method: str) -> None:
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method.upper() + path
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
        return {
            **self.headers[KucoinFutures.TYPE.private],
            'KC-API-SIGN': signature,
            'KC-API-TIMESTAMP': str(now),
        }

    def _request(self, type, method, path, data=None):
        if type == KucoinFutures.TYPE.public:
            headers = self.headers[KucoinFutures.TYPE.public]
        else:
            headers = self._signed_headers(path, method)
        response = requests.request(
            method=method,
            url=self.base_url + path,
            data=data,
            headers=headers,
        )
        response.raise_for_status()
        response = response.json()
        if not response['code'] == '200000':
            raise KucoinFuturesError(response['code'])
        return response

    @LimitGuard('100/s')
    @LimitGuard('50/s', key='market_id')
    def place_order(self, **order: OrderParams) -> OrderParams:
        return self._request(
            type=KucoinFutures.TYPE.private,
            method=KucoinFutures.METHOD.post,
            path='',
            # data=Serializer
        )
        raise NotImplementedError()

    def cancel_order(self, exchange_id: int) -> None:
        raise NotImplementedError()

    def get_order_detail(self, exchange_id: int) -> OrderParams:
        raise NotImplementedError()
