from datetime import datetime
from decimal import Decimal
from typing import Optional, TypedDict

class OrderParams(TypedDict):
    client_order_id: int
    market_id: int
    status_id: int
    timestamp: datetime
    price: Optional[Decimal]
    volume: Optional[Decimal]
    is_sell: bool

class BaseClient:
    def __init__(self, token, credentials) -> None:
        raise NotImplementedError()

    def place_order(self, amount, price, ) -> None:
        raise NotImplementedError()

    def cancel_order(self, amount, price, ) -> None:
        raise NotImplementedError()

    def get_order_status(self, amount, price, ) -> None:
        raise NotImplementedError()
