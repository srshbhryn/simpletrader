import time
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, TypedDict

import requests

logger = logging.getLogger('django')


class ExchangeClientError(Exception):
    pass


class FillParams(TypedDict):
    exchange_id: str
    exchange_order_id: str
    market_id: int
    timestamp: datetime
    price: Decimal
    volume: Decimal
    is_sell: bool
    fee: Decimal
    fee_asset_id: int


class OrderParams(TypedDict):
    exchange_id: str
    client_order_id: Optional[str]
    market_id: int
    status_id: int
    timestamp: datetime
    leverage: Optional[int]
    price: Optional[Decimal]
    volume: Optional[Decimal]
    is_sell: bool


class BaseClient:
    class TYPE:
        public = 0
        private = 1

    class METHOD:
        get = 'get'
        post = 'post'
        delete = 'delete'

    def __init__(self, credentials: dict, token: str) -> None:
        raise NotImplementedError()

    # TODO add get fills.

    def place_order(self, order: OrderParams) -> OrderParams:
        raise NotImplementedError()

    def cancel_order(self, exchange_id: int) -> None:
        raise NotImplementedError()

    def get_order_detail(self, exchange_id: int) -> OrderParams:
        raise NotImplementedError()


def handle_exception(func):
    def wrapper(*args, **kwargs):
        self: BaseClient = args[0]
        while True:
            try:
                response = func(*args, **kwargs)
            except requests.RequestException as e:
                if e.response and e.response.status_code == 403:
                    self.initialize()
                    continue
                elif e.response and e.response.status_code == 400:
                    logger.info(e)
                    raise ExchangeClientError(e)
            except Exception as e:
                logger.error(e)
                time.sleep(10)
            return response
    return wrapper
