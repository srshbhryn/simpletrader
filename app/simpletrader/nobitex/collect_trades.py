
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
