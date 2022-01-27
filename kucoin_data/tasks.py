import logging

from celery import shared_task

from kucoin_data.clients import get_spot_client, get_futures_client
from kucoin_data.journals import SpotOrderBookJournal, SpotTradeJournal, FuturesOrderBookJournal, FuturesTradeJournal

log = logging.getLogger('django')


@shared_task(name='kucoin_data.collect.spot_orders', ignore_result=True, store_errors_even_if_ignored=True)
def collect_spot_orders(symbol, market_id):
    client = get_spot_client()
    journal = SpotOrderBookJournal()
    try:
        response = client.get_aggregated_orderv3(symbol)
        timestamp = int(response['time'] / 10**6)
        for order in response['bids']:
            journal.append_line({
                'market_id': market_id,
                'time': timestamp,
                'price': order[0],
                'volume': order[1],
                'is_bid': True,
            })
        for order in response['asks']:
            journal.append_line({
                'market_id': market_id,
                'time': timestamp,
                'price': order[0],
                'volume': order[1],
                'is_bid': False,
            })
    except Exception as e:
        log.error(f'Getting Spot Orders for {symbol} Failed: {e}')
        raise e


@shared_task(name='kucoin_data.collect.spot_trades', ignore_result=True, store_errors_even_if_ignored=True)
def collect_spot_trades(symbol, market_id):
    client = get_spot_client()
    journal = SpotTradeJournal()
    try:
        response = client.get_trade_histories(symbol)
        for trade in response:
            journal.append_line({
                'market_id': market_id,
                'time': int(trade['time'] / 10**6),
                'sort_field': int(trade['sequence']),
                'price': trade['price'],
                'volume': trade['size'],
                'is_buyer_maker': trade['side'] == 'sell',
            })
    except Exception as e:
        log.error(f'Getting Spot Trades for {symbol} Failed: {e}.')
        raise e

@shared_task(name='kucoin_data.collect.futures_orders', ignore_result=True, store_errors_even_if_ignored=True)
def collect_futures_orders(symbol, market_id):
    client = get_futures_client()
    journal = FuturesOrderBookJournal()
    try:
        response = client.l2_order_book(symbol)
        timestamp = int(response['ts'] / 10**6)
        for order in response['bids']:
            journal.append_line({
                'market_id': market_id,
                'time': timestamp,
                'price': order[0],
                'volume': order[1],
                'is_bid': True,
            })
        for order in response['asks']:
            journal.append_line({
                'market_id': market_id,
                'time': timestamp,
                'price': order[0],
                'volume': order[1],
                'is_bid': False,
            })
    except Exception as e:
        log.error(f'Getting futures orders for {symbol} failed: {e}')
        raise e
    else:
        log.info(f'Got futures orders for {symbol} successfully.')


@shared_task(name='kucoin_data.collect.futures_trades', ignore_result=True, store_errors_even_if_ignored=True)
def collect_futures_trades(symbol, market_id):
    client = get_futures_client()
    journal = FuturesTradeJournal()
    try:
        response = client.get_trade_history(symbol)
        for trade in response:
            journal.append_line({
                'market_id': market_id,
                'time': int(trade['ts'] / 10**6),
                'sort_field': int(trade['sequence']),
                'price': trade['price'],
                'volume': trade['size'],
                'is_buyer_maker': trade['side'] == 'sell',
            })
    except Exception as e:
        log.error(f'Getting futures orders for {symbol} failed: {e}')
        raise e
    else:
        log.info(f'Got futures orders for {symbol} successfully.')


journals = [
    # SpotOrderBookJournal,
    SpotTradeJournal,
    # FuturesOrderBookJournal,
    FuturesTradeJournal,
]

@shared_task(name='kucoin_data.store.orders_and_trades', ignore_result=True, store_errors_even_if_ignored=True)
def store_orders_and_trades():
    for journal_idx, _ in enumerate(journals):
        _store.delay(journal_idx)

@shared_task(name='kucoin_data.store._store', ignore_result=True, store_errors_even_if_ignored=True)
def _store(journal_idx):
    journals[journal_idx]().insert_to_db()
