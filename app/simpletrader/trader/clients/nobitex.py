from typing import Dict

import time
from datetime import datetime
import logging
import requests
import pyotp
from decimal import Decimal

from simpletrader.base.utils import LimitGuard
from simpletrader.trader.sharedconfigs import Market, Asset, OrderState

from .base import OrderParams
from .helpers.nobitex import translate_currency, translate_order_status


logger = logging.getLogger('django')


class NobitexClientError(Exception):
    pass


class Serializers:
    @classmethod
    def serialize_fill(self, fill: dict) -> dict:
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

    @classmethod
    def serialize_order(self, order: dict) -> dict:
        base_asset = Asset.get_by('name',
            translate_currency(order['srcCurrency']),
        )
        quote_asset = Asset.get_by('name',
            translate_currency(order['dstCurrency']),
        )
        markets = Market.get_by('base_asset', base_asset)
        if isinstance(markets, list):
            market = [
                m for m in markets
                if m.quote_asset == quote_asset
            ][0]
        else:
            market = markets
        _order = {
            'exchange_id': order['id'],
            'market_id': market.id,
            'is_sell': order['type'] == 'sell',
            'volume': Decimal(order['amount']),
            'timestamp': datetime.fromisoformat(order['created_at']),
            'status_id': OrderState.get_by('name',
                translate_order_status(order['status'])
            ).id,
        }
        if 'price' in order:
            _order['price'] = Decimal(order['price'])
        return _order

    @classmethod
    def deserialize_order(self, order: dict) -> dict:
        market = Market.get_by('id', order['market_id'])
        base_asset = market.base_asset.name
        quote_asset = market.quote_asset.name
        _order = {
            'type': 'sell' if order['is_sell'] else 'buy',
            'srcCurrency': base_asset,
            'dstCurrency': quote_asset,
            'amount': str(order['volume']),
        }
        price = order.get('price')
        if price is None:
            _order['execution'] = 'market'
        else:
            _order['price'] = price
        return _order


def handle_exception(func):
    def wrapper(*args, **kwargs):
        self: Nobitex = args[0]
        while True:
            try:
                response = func(*args, **kwargs)
            except requests.RequestException as e:
                if e.response and e.response.status_code == 403:
                    self.initialize()
                    continue
                elif e.response and e.response.status_code == 400:
                    logger.info(e)
                    return None
            except Exception as e:
                time.sleep(10)
            return response
    return wrapper



class Nobitex:
    base_url = 'https://api.nobitex.ir'

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
        self.sessions: Dict[int,requests.Session] = {
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
            url=self.base_url+'/auth/login/',
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

    def _request(self, type, method, url, data=None):
        response = self.sessions[type].request(
            method=method,
            url=url,
            data=data,
        )
        response.raise_for_status()
        response = response.json()
        if not response['status'] == 'ok':
            raise NobitexClientError(response['message'])
        return response

    @LimitGuard('20/ms')
    def get_fills(self, from_id: int = None):
        params = ''
        if from_id:
            params = f'?from_id={from_id}'
        return [
            Serializers.serialize_fill(f)
            for f in self._request(
                self.TYPE.private,
                self.METHOD.get,
                self.base_url + '/market/trades/list' + params,
                None
            )['trades']
        ]

    # @LimitGuard('30/m')
    # def get_orders(self, from_id: int = None) -> dict:
    #     params = ''
    #     if from_id:
    #         params = f'?from_id={from_id}'
    #     return [
    #         Serializers.serialize_order(order)
    #         for order in self._request(
    #             self.TYPE.private,
    #             self.METHOD.get,
    #             self.base_url + '/market/orders/list' + params,
    #             None
    #         )['orders']
    #     ]

    @LimitGuard('200/10m')
    def place_order(self, **order: OrderParams):
        return Serializers.serialize_order(
            self._request(
                self.TYPE.private,
                self.METHOD.post,
                self.base_url + '/market/orders/add',
                Serializers.deserialize_order(order)
            )
        )

    @LimitGuard('60/m')
    def get_order_detail(self, exchange_id: int):
        return Serializers.serialize_order(
            self._request(
                self.TYPE.private,
                self.METHOD.post,
                self.base_url + '/market/orders/status',
                Serializers.deserialize_order({'id': exchange_id})
            )
        )

    @LimitGuard('30/m')
    def cancel_order(self, exchange_id: int) -> None:
        self._request(
            self.TYPE.private,
            self.METHOD.post,
            self.base_url + '/market/orders/update-status',
            Serializers.deserialize_order({'id': exchange_id, 'status': 'canceled'})
        )
