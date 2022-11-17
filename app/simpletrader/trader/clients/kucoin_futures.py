from typing import TypedDict, Dict, List, Optional
from decimal import Decimal
from datetime import datetime
import json
import uuid
import base64
import hmac
import hashlib
import requests
import logging
import time

from django.utils.timezone import now, make_aware

from simpletrader.base.utils import LimitGuard
from simpletrader.trader.sharedconfigs import Market, Exchange, OrderState
from .base import OrderParams, ExchangeClientError, BaseClient, handle_exception, FillParams
from .helpers.kucoin_futures import get_symbol, translate_symbol, get_fee_asset_id


exchange_id = Exchange.get_by('name', 'kucoin_futures').id

logger = logging.getLogger('django')


class KucoinFuturesError(ExchangeClientError):
    pass


class Symbol(str):
    pass


class ContractInfo(TypedDict):
    symbol: str
    rootSymbol: str
    baseCurrency: str
    quoteCurrency: str
    settleCurrency: str
    maxOrderQty: int
    lotSize: int
    maxPrice: Decimal
    tickSize: Decimal
    indexPriceTickSize: Decimal
    multiplier: Decimal
    makerFeeRate: Decimal
    takerFeeRate: Decimal
    isDeleverage: bool
    isInverse: bool
    fundingFeeRate: float
    maxLeverage: int


class Serializer:
    contract_info_map: Dict[Symbol, ContractInfo] = {}

    @classmethod
    def serialize_fill(cls, fill: dict) -> FillParams:
        symbol = fill['symbol']
        market = Market.get_by('symbol', symbol)
        volume = fill['size'] * cls.contract_info_map[symbol]['multiplier']
        is_sell = fill['side'] == 'sell'
        return {
            'external_id': fill['tradeId'],
            'external_order_id': fill['orderId'],
            'market_id': market.id,
            'timestamp': make_aware(datetime.fromtimestamp(fill['tradeTime'] / 10**9)),
            'is_sell': is_sell,
            'price': Decimal(str(fill['price'])),
            'volume': volume,
            'fee': Decimal(str(fill['fee'])),
            'fee_asset_id': get_fee_asset_id(fill['feeCurrency']),
            'exchange_id': exchange_id,
        }

    @classmethod
    def serialize_contract_info(cls, contract_info) -> ContractInfo:
        decimal_keys = [
            'maxPrice',
            'tickSize',
            'indexPriceTickSize',
            'multiplier',
            'makerFeeRate',
            'takerFeeRate',
        ]
        return {
            **{
                k: v
                for k, v in contract_info.items()
                if k not in decimal_keys
            },
            **{
                k: Decimal(str(contract_info[k]))
                for k in decimal_keys
            }
        }

    @classmethod
    def serialize_order(cls, order: dict) -> OrderParams:
        return {
            'external_id': order['orderId'],
            'timestamp': now(),
            'status_id': OrderState.get_by('name','open_no_fill').id,
            'exchange_id': exchange_id,
        }

    @classmethod
    def deserialize_order(cls, order: OrderParams) -> dict:
        symbol = get_symbol(order['market_id'])
        contract_info: ContractInfo = cls.contract_info_map[symbol]
        contract_info['multiplier']
        if not order['leverage']:
            order['leverage'] = 10

        #fix amount
        amount = order['volume']
        size = round(amount / contract_info['multiplier'], 0)
        order['volume'] = size * contract_info['multiplier']

        #fix price
        price = order['price']
        if price is not None:
            tick_size = contract_info['tickSize']
            price = round(price / tick_size, 0) * tick_size
            order['price'] = price

        # MARKET ORDER PARAMETERS
        return {
            # Integer	[optional] amount of contract to buy or sell
            'size': int(size),
            # String	Limit price
            **({'price': float(price)} if price else {}),
            #String	Unique order id created by users to identify their orders, e.g. UUID, Only allows numbers, characters, underline(_), and separator(-)
            'clientOid': order['client_order_id'],
            #String	buy or sell
            'side': 'sell' if order['is_sell'] else 'buy',
            #String	a valid contract code. e.g. XBTUSDM
            'symbol': symbol,
            #String	[optional] Either limit or market
            'type': 'limit' if price else 'market',
            #String	Leverage of the order
            'leverage': order['leverage'],
            #String	[optional] remark for the order, length cannot exceed 100 utf8 characters
            # 'remark': None,
            #String	[optional] Either down or up. Requires stopPrice and stopPriceType to be defined
            # 'stop': None,
            #String	[optional] Either TP, IP or MP, Need to be defined if stop is specified.
            # 'stopPriceType': None,
            #String	[optional] Need to be defined if stop is specified.
            # 'stopPrice': None,
            #boolean	[optional] A mark to reduce the position size only. Set to false by default. Need to set the position size when reduceOnly is true.
            # 'reduceOnly': None,
            #boolean	[optional] A mark to close the position. Set to false by default. It will close all the positions when closeOrder is true.
            # 'closeOrder': None,
            #boolean	[optional] A mark to forcely hold the funds for an order, even though it's an order to reduce the position size. This helps the order stay on the order book and not get canceled when the position size changes. Set to false by default.
            # 'forceHold': None,
        }


class KucoinFutures(BaseClient):
    base_url = 'https://api-futures.kucoin.com'

    def __init__(self, credentials: dict, token: str):
        self.bot_token  = token
        self.api_key = credentials['api_key']
        self.api_secret = credentials['api_secret']
        self.api_passphrase = credentials['api_passphrase']
        self.headers: Dict[int, Dict] = {
            self.TYPE.public: {},
            self.TYPE.private: {},
        }
        self.headers[self.TYPE.public] = {
            'content-type': 'application/json',
        }
        passphrase = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.api_passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        )
        self.headers[self.TYPE.private] = {
            **self.headers[self.TYPE.public],
            'KC-API-KEY': self.api_key,
            'KC-API-KEY-VERSION': '2',
            'KC-API-PASSPHRASE': passphrase,
        }
        if not Serializer.contract_info_map:
            Serializer.contract_info_map = {
                contract_info['symbol']: Serializer.serialize_contract_info(contract_info)
                for contract_info in self._request(
                    self.TYPE.public,
                    self.METHOD.get,
                    '/api/v1/contracts/active',
                )
                if translate_symbol(contract_info['symbol']) is not None
            }


    def _set_sand_box(self):
        pass

    def _signed_headers(self, path: str, method: str, data: Optional[str] = None) -> dict:
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method.upper() + path + data
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                str_to_sign.encode('utf-8'),
                hashlib.sha256,
            ).digest()
        )
        return {
            **self.headers[self.TYPE.private],
            'KC-API-SIGN': signature,
            'KC-API-TIMESTAMP': str(now),
        }

    @handle_exception
    def _request(self, type, method, path, data:Optional[str] = None) -> Dict:
        data = data or ''
        if type == self.TYPE.public:
            headers = self.headers[self.TYPE.public]
        else:
            headers = self._signed_headers(path, method, data)
        response = requests.request(
            method=method,
            url=self.base_url + path,
            data=data,
            headers=headers,
        )
        response.raise_for_status()
        response = response.json()
        if not response['code'] == '200000':
            raise KucoinFuturesError(response['code'], response)
        return response['data']

    @LimitGuard('30/3s')
    def place_order(self, order: OrderParams) -> str:
        order['client_order_id'] = f'{self.bot_token}_{uuid.uuid4().hex}'
        return {
            **order,
            **Serializer.serialize_order(
                self._request(
                    type=KucoinFutures.TYPE.private,
                    method=KucoinFutures.METHOD.post,
                    path='/api/v1/orders',
                    data=json.dumps(Serializer.deserialize_order(order)).strip(),
                )
            ),
        }

    @LimitGuard('40/3s')
    def cancel_order(self, external_id: str) -> None:
        self._request(
            type=KucoinFutures.TYPE.private,
            method=KucoinFutures.METHOD.delete,
            path=f'/api/v1/orders/{external_id}'
        )

    def get_fills(self, from_timestamp: Optional[datetime] = None) -> List[FillParams]:
        from_timestamp = int(from_timestamp.timestamp() * 1000)
        has_next = True
        trades = []
        page = 1
        while has_next:
            fetched_trades, has_next = self._get_fills(from_timestamp, page)
            trades += fetched_trades
            page += 1
        return trades

    @LimitGuard('9/3s')
    def _get_fills(self, from_timestamp: Optional[datetime] = None, page: int = None):
        params = '?pageSize=100'
        if from_timestamp:
            params += f'&startAt={from_timestamp}'
        if page:
            params += f'&currentPage={page}'
        response = self._request(
            type=KucoinFutures.TYPE.private,
            method=KucoinFutures.METHOD.get,
            path='/api/v1/fills' + params,
        )
        has_next = response['totalPage'] > response['currentPage']
        return [
            Serializer.serialize_fill(f)
            for f in response['items']
        ], has_next

    def get_order_detail(self, exchange_id: int) -> OrderParams:
        raise NotImplementedError()


# class StreamClient:
#     pass