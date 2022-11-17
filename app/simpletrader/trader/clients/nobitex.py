from typing import Dict, List

import functools
import time
from datetime import datetime
import logging
import requests
import pyotp
from decimal import Decimal

from django.utils.timezone import now, make_aware

from simpletrader.base.utils import LimitGuard
from simpletrader.trader.sharedconfigs import Market, Asset, OrderState, ASSETS, Exchange

from .base import OrderParams, ExchangeClientError, BaseClient, handle_exception, FillParams, \
    WalletSnapShotParams
from .helpers.nobitex import translate_currency, translate_order_status


logger = logging.getLogger('django')


class NobitexClientError(ExchangeClientError):
    pass


class Serializers:
    @classmethod
    def serialize_fill(self, fill: dict) -> FillParams:
        symbol = fill['market'].replace('-', '').replace('RLS', 'IRT')
        market = Market.get_by('symbol', symbol)
        is_sell = fill['type'] == 'sell'
        fee_asset_id = market.quote_asset.id if is_sell else market.base_asset.id
        return {
            'external_id': fill['id'],
            'external_order_id': fill['orderId'],
            'market_id': market.id,
            'timestamp': make_aware(datetime.fromisoformat(fill['timestamp'])),
            'is_sell': is_sell,
            'price': Decimal(str(fill['price'])),
            'volume': Decimal(str(fill['amount'])),
            'fee': Decimal(str(fill['fee'])),
            'fee_asset_id': fee_asset_id,
            'exchange_id': Exchange.get_by('name', 'nobitex').id,
        }

    @classmethod
    def serialize_order(self, order: dict) -> OrderParams:
        symbol = order['market'].replace('-', '').replace('RLS', 'IRT')
        market = Market.get_by('symbol', symbol)
        _order = {
            'external_id': order['id'],
            'market_id': market.id,
            'is_sell': order['type'] == 'sell',
            'volume': Decimal(order['amount']),
            'timestamp': datetime.fromisoformat(order['created_at']),
            'status_id': OrderState.get_by('name',
                translate_order_status(order['status'])
            ).id,
            'exchange_id': 1,
        }
        if 'price' in order:
            _order['price'] = Decimal(order['price'])
        return _order

    @classmethod
    def serialize_balances(cls,
        currency_codename: str,
        balances: dict,
        timestamp: datetime,
    ) -> WalletSnapShotParams:
        balance=Decimal(balances['balance'])
        blocked_balance=Decimal(balances['blocked'])
        free_balance = balance - blocked_balance
        return WalletSnapShotParams(
            asset_id=Asset.get_by('name', currency_codename.lower()).id,
            timestamp=timestamp,
            blocked_balance=blocked_balance,
            free_balance=free_balance,
        )

    @classmethod
    def deserialize_order(cls, order: OrderParams) -> dict:
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
            _order['execution'] = 'limit'
            _order['price'] = str(price)
        return _order


class Nobitex(BaseClient):
    base_url = 'https://api.nobitex.ir'

    def __init__(self, credentials: dict, token: str) -> None:
        self.credentials = credentials
        self.bot_token = token
        self.token = None
        self.initialize()

    def initialize(self) -> None:
        credentials: dict = self.credentials
        token: str = self.token
        while self.token is None:
            try:
                # self.token: str = self._get_token(credentials)
                self.token: str = credentials['token']
            except Exception as e:
                logger.info(e)
        self.sessions: Dict[int,requests.Session] = {
            Nobitex.TYPE.public: requests.Session(),
            Nobitex.TYPE.private: requests.Session(),
        }
        self.sessions[Nobitex.TYPE.public].headers = {
            'content-type': 'application/json',
            'user-agent': f'TraderBot/{self.bot_token}'
        }
        self.sessions[Nobitex.TYPE.private].headers = {
            **self.sessions[Nobitex.TYPE.public].headers,
            'Authorization': f'Token {self.token}'
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
            'x-totp': pyotp.TOTP(credentials['totp_key']).now(),
            'user-agent': f'TraderBot/{self.bot_token}',
        }
        response = requests.post(
            url=self.base_url+'/auth/login/',
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        response.json()['key']

    @handle_exception
    def _request(self, type, method, url, data=None):
        response = self.sessions[type].request(
            method=method,
            url=url,
            json=data,
        )
        response.raise_for_status()
        response = response.json()
        if not response['status'] == 'ok':
            raise NobitexClientError(response)
        return response

    def get_fills(self, from_id: int = None) -> List[FillParams]:
        has_next = True
        trades = []
        page = 1
        while has_next:
            fetched_trades, has_next = self._get_fills(from_id, page)
            trades += fetched_trades
            page += 1
        return trades

    @LimitGuard('20/m')
    def _get_fills(self, from_id: int = None, page: int = None):
        params = '?pageSize=100'
        if from_id:
            params += f'&fromId={from_id}'
        if page:
            params += f'&page={page}'
        response = self._request(
                self.TYPE.private,
                self.METHOD.get,
                self.base_url + '/market/trades/list' + params,
                None
            )
        return [
            Serializers.serialize_fill(f)
            for f in response['trades']
        ], response['hasNext']

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
    def place_order(self, order: OrderParams) -> OrderParams:
        return Serializers.serialize_order(
            self._request(
                self.TYPE.private,
                self.METHOD.post,
                self.base_url + '/market/orders/add',
                Serializers.deserialize_order(order)
            )['order']
        )

    @LimitGuard('60/m')
    def get_order_detail(self, exchange_id: int) -> OrderParams:
        return Serializers.serialize_order(
            self._request(
                self.TYPE.private,
                self.METHOD.post,
                self.base_url + '/market/orders/status',
                {'id': exchange_id},
            )
        )

    @LimitGuard('30/m')
    def cancel_order(self, external_id: int) -> None:
        self._request(
            self.TYPE.private,
            self.METHOD.post,
            self.base_url + '/market/orders/update-status',
            {'order': int(external_id), 'status': 'canceled'},
        )

    @functools.cached_property
    def _wallet_currencies(self):
        return ','.join([
            a.name
            for a in ASSETS
        ])

    @LimitGuard('12/m')
    def get_balances(self) -> List[WalletSnapShotParams]:
        timestamp: datetime = now()
        return [
            Serializers.serialize_balances(
                currency_codename,
                balances,
                timestamp,
            )
            for currency_codename, balances in self._request(
                self.TYPE.private,
                self.METHOD.get,
                self.base_url + f'/v2/wallets?currencies={self._wallet_currencies}'
            )['wallets'].items()
        ]
