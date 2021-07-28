import logging

from celery import shared_task

from .models import MarketData, MarketTrades
from .client import Client
from .journals import marketdata_journal, trade_journal

log = logging.getLogger('binance')
client = Client()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def collect_market_data(symbol, market_id):

    log.info(f'getting market data for {symbol}.')
    try:
        response = client.get_orderbook(symbol)
        for md in response['bids']:
            marketdata_journal.append_line({
                'market_id': market_id,
                'price': md['price'],
                'volume': md['volume'],
                'is_buy': 0,
            })
        for md in response['asks']:
            marketdata_journal.append_line({
                'market_id': market_id,
                'price': md['price'],
                'volume': md['volume'],
                'is_buy': 1,
            })
    except Exception as e:
        log.error(f'getting market data for {symbol} fialed: {e}')
        raise e
    else:
        log.info(f'got market data for {symbol} succesfuly.')


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def collect_market_trades(symbol, market_id):

    log.info(f'getting trades for {symbol}.')
    try:
        response = client.get_trades(symbol)
        for md in response['trades']:
            trade_journal.append_line({
                'market_id': market_id,
                'time': md['time'],
                'price': md['price'],
                'volume': md['volume'],
                'is_buy': md['is_buy'],
            })
    except Exception as e:
        log.error(f'getting trades for {symbol} fialed: {e}')
        raise e
    else:
        log.info(f'got trades for {symbol} succesfuly.')


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def store_market_data():
    marketdata_journal.bulk_create_old_files()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def store_trades():
    trade_journal.bulk_create_old_files()
