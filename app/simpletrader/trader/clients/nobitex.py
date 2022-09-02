import time
from datetime import datetime
import logging
import requests
import pyotp
from decimal import Decimal

from simpletrader.trader.sharedconfigs import Market

class NobitexClientError(Exception):
    pass


logger = logging.getLogger('django')


def handle_exception(func):
    def wrapper(*args, **kwargs):
        self: Nobitex = args[0]
        while True:
            try:
                response = func(*args, **kwargs)
                success = True
            except requests.RequestException as e:
                if e.response and e.response.status_code == 403:
                    self.initialize()
                    continue
                elif e.response and e.response.status_code == 400:
                    self.
            except Exception as e:
                time.sleep(10)
            return response
    return wrapper



class Nobitex:
    base_url = 'https://api.nobitex.ir/'

    def __init__(self, credentials: dict, token: str) -> None:
        self.credentials = credentials
        self.token = token

    def initialize(self) -> None:
        credentials: dict = self.credentials
        token: str = self.token
        while self.token is None:
            try:
                self.token: str = self.get_token(credentials)
            except Exception as e:
                logger.info(e)
        self.sessions = {
            Nobitex.TYPE.public: requests.Session(),
            Nobitex.TYPE.private: requests.Session(),
        }
        self.sessions[Nobitex.TYPE.public].headers = {
            'content-type': 'application/json',
            'user-agent': f'TraderBot/{token}'
        }
        self.sessions[Nobitex.TYPE.public].headers = {
            **self.sessions[Nobitex.TYPE.public].headers,
            'authorization': f'Token {token}'
        }

    def _get_token(self, credentials) -> str:
        body = {
            'username': credentials['username'],
            'password': credentials['password'],
            'captcha': 'api',
            'remember': 'yes',

        }
        headers = {
            'content-type': 'application/json',
            'x-totp': pyotp.TOTP(credentials['totp_key']).now()
        }
        response = requests.post(
            url='https://api.nobitex.ir/auth/login/',
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        response.json()['key']

    class TYPE:
        public = 0
        private = 1

    class METHOD:
        get = 'get'
        post = 'post'

    def _request(self, type, method, path, body=None):
        response = self.sessions[type].__getattribute__(method)(
            url=f'{self.base_url}{path}'
            json=body,
        )
        response.raise_for_status()
        response = response.json()
        if not response['status'] == 'ok':
            raise NobitexClientError(response['message'])
        return response

    def get_fills(self, from_id: int = None) -> dict:
        params = ''
        if from_id:
            params = f'?from_id={from_id}'
        return [
            self._serialize_fill(f)
            for f in self._request(
                self.TYPE.private,
                self.METHOD.get,
                self.base_url + '/' + params,
                {}
            )['trades']
        ]

    def _serialize_fill(self, fill: dict):
        market: Market = Market.get_by('symbol', fill['market'])
        is_sell = fill['type'] == 'sell'
        fee_asset_id = market.quote_asset.id if is_sell else market.base_asset.id
        return {
            'exchange_id': fill['id'],
            'exchange_order_id': fill['orderId'],
            'market_id': market.id,
            'timestamp': datetime.fromisoformat(fill['timestamp']),
            'is_sell': is_sell,
            'price': Decimal(fill['price']),
            'volume': Decimal(fill['price']),
            'fee': Decimal(fill['fee']),
            'fee_asset_id': fee_asset_id

        }

