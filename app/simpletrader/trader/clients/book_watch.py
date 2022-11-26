import functools
import decimal

from django.conf import settings

@functools.lru_cache(maxsize=None)
def _get_redis():
    from redis import Redis
    return Redis(
        host=settings.BOOK_WATCH_REDIS_HOST,
        port=settings.BOOK_WATCH_REDIS_PORT,
        db=settings.BOOK_WATCH_REDIS_DB_NO,
    )



# ts, best_ask, best_ask_volume, best_bid_price
def get_best_price(market_id: int, is_sell: bool):
    '''is_sell: true => user want to sell with market order
    '''
    _, best_ask_price, _, best_bid_price, _ = _get_redis().get(
        name=f'{market_id}',
    ).decode('utf-8').split(',')
    return decimal.Decimal(
        best_bid_price
        if is_sell else
        best_ask_price
    )
