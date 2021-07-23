import logging
from os import sync

from celery import shared_task

from .models import Market, MarketData, MarketTrades
from .client import Client

log = logging.getLogger('binance')
client = Client()
# markets = Market.objects.all()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def collect_market_data(symbol, market_id):

    log.info(f'getting market data for {symbol}.')
    try:
        response = client.get_orderbook(symbol)
        MarketData.objects.bulk_create([
            MarketData(
                market_id = market_id,
                price = md['price'],
                volume = md['volume'],
                is_buy = False
            )
            for md in response['bids']
        ]+[
            MarketData(
                market_id = market_id,
                price = md['price'],
                volume = md['volume'],
                is_buy = True
            )
            for md in response['asks']
        ])

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
        MarketTrades.objects.bulk_create([
            MarketTrades(
                market_id = market_id,
                time = md['time'],
                price = md['price'],
                volume = md['volume'],
                is_buy = md['is_buy'],
            )
            for md in response['trades']
        ])
    except Exception as e:
        log.error(f'getting trades for {symbol} fialed: {e}')
        raise e
    else:
        log.info(f'got trades for {symbol} succesfuly.')
