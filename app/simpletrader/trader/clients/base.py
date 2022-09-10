from datetime import datetime
from decimal import Decimal
from typing import Optional, TypedDict

class ExchangeClientError(Exception):
    pass

class OrderParams(TypedDict):
    client_order_id: int
    market_id: int
    status_id: int
    timestamp: datetime
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

    def __init__(self, credentials: dict, token: str) -> None:
        raise NotImplementedError()

    def place_order(self, order: OrderParams) -> OrderParams:
        raise NotImplementedError()

    def cancel_order(self, exchange_id: int) -> None:
        raise NotImplementedError()

    def get_order_detail(self, exchange_id: int) -> OrderParams:
        raise NotImplementedError()
