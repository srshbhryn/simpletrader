
from functools import lru_cache
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware
import redis


@lru_cache(maxsize=2)
def _get_redis():
    return redis.Redis(
        host=settings.BOOK_WATCH_REDIS_HOST,
        port=int(settings.BOOK_WATCH_REDIS_PORT),
        db=int(settings.BOOK_WATCH_REDIS_DB_NO),
    )


class Book:
    def __init__(
        self,
        timestamp,
        best_ask_price,
        best_ask_volume,
        best_bid_price,
        best_bid_volume,
    ) -> None:
        self.timestamp = timestamp
        self.best_ask_price = best_ask_price
        self.best_ask_volume = best_ask_volume
        self.best_bid_price = best_bid_price
        self.best_bid_volume = best_bid_volume


def get_book(market_id):
    book = _get_redis().get(str(market_id))
    if book is None:
        return None
    (
        timestamp,
        best_ask_price,
        best_ask_volume,
        best_bid_price,
        best_bid_volume,
    ) = book.split(',')
    timestamp = make_aware(datetime.fromtimestamp(int(timestamp) / 1000))
    best_ask_price = float(best_ask_price)
    best_ask_volume = float(best_ask_volume)
    best_bid_price = float(best_bid_price)
    best_bid_volume = float(best_bid_volume)
    return Book(
        timestamp,
        best_ask_price,
        best_ask_volume,
        best_bid_price,
        best_bid_volume,
    )
