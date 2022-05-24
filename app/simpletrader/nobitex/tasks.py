import time
import logging

from celery import shared_task


from simpletrader.nobitex.client import get_client
from simpletrader.nobitex.journals import OrderJournal, TradeJournal

log = logging.getLogger('django')
# client = Client()


@shared_task(name='nobitex.collect.orders', ignore_result=True, store_errors_even_if_ignored=True)
def collect_orders(symbol, market_id):
    log.info(f'getting market data for {symbol}.')
    client = get_client()
    journal = OrderJournal()
    try:
        response = client.get_orderbook(symbol)
        timestamp = int(time.time() * 1000)
        for md in response['bids']:
            journal.append_line({
                'market_id': market_id,
                'price': md['price'],
                'volume': md['volume'],
                'is_bid': False,
                'time': timestamp,
            })
        for md in response['asks']:
            journal.append_line({
                'market_id': market_id,
                'price': md['price'],
                'volume': md['volume'],
                'is_bid': True,
                'time': timestamp,
            })
    except Exception as e:
        log.error(f'getting market data for {symbol} fialed: {e}')
        raise e
    else:
        log.info(f'got market data for {symbol} succesfuly.')


@shared_task(name='nobitex.collect.trades', ignore_result=True, store_errors_even_if_ignored=True)
def collect_trades(symbol, market_id):
    log.info(f'getting trades for {symbol}.')
    client = get_client()
    journal = TradeJournal()
    try:
        response = client.get_trades(symbol)
        for md in response['trades']:
            journal.append_line({
                'market_id': market_id,
                'time': md['time'],
                'price': md['price'],
                'volume': md['volume'],
                'is_buyer_maker': md['is_buy'],
            })

    except Exception as e:
        log.error(f'getting trades for {symbol} failed: {e}')
    else:
        log.info(f'got trades for {symbol} successfully.')


@shared_task(name='nobitex.store.orders', ignore_result=True, store_errors_even_if_ignored=True)
def store_orders():
    journal = OrderJournal()
    journal.bulk_create_old_files()

@shared_task(name='nobitex.store.trades', ignore_result=True, store_errors_even_if_ignored=True)
def store_trades():
    journal = TradeJournal()
    journal.bulk_create_old_files()
