ASSETS = [
    ('BTC', 'XBT'),
    ('USDT', 'USDTM'),
    ('BNB', 'BNB',),
    ('ETH', 'ETH',),
    ('ADA', 'ADA',),
    ('DOGE', 'DOGE',),
    ('DOT', 'DOT',),
    ('AVAX', 'AVAX',),
    ('MATIC', 'MATIC',),
    ('XRP', 'XRP',),
    ('TRX', 'TRX',),
    ('AAVE', 'AAVE',),
    ('SHIB', 'SHIB',),
    ('ETC', 'ETC',),
    ('BCH', 'BCH',),
    ('LTC', 'LTC',),
    ('UNI', 'UNI',),
    ('LUNA', 'LUNA',),
    ('LINK', 'LINK',),
    ('SOL', 'SOL',),
]
SPOT_MARKETS = [
    ('BTC', 'USDT'),
    ('BNB', 'USDT',),
    ('ETH', 'USDT',),
    ('ADA', 'USDT',),
    ('DOGE', 'USDT',),
    ('DOT', 'USDT',),
    ('AVAX', 'USDT',),
    ('MATIC', 'USDT',),
    ('XRP', 'USDT',),
    ('TRX', 'USDT',),
    ('AAVE', 'USDT',),
    ('SHIB', 'USDT',),
    ('ETC', 'USDT',),
    ('BCH', 'USDT',),
    ('LTC', 'USDT',),
    ('UNI', 'USDT',),
    ('LUNA', 'USDT',),
    ('LINK', 'USDT',),
    ('SOL', 'USDT',),
]
FUTURES_CONTRACTS = [
    ('XBT', 'USDTM'),
    ('BNB', 'USDTM',),
    ('ETH', 'USDTM',),
    ('ADA', 'USDTM',),
    ('DOGE', 'USDTM',),
    ('DOT', 'USDTM',),
    ('AVAX', 'USDTM',),
    ('MATIC', 'USDTM',),
    ('XRP', 'USDTM',),
    ('TRX', 'USDTM',),
    ('AAVE', 'USDTM',),
    ('SHIB', 'USDTM',),
    ('ETC', 'USDTM',),
    ('BCH', 'USDTM',),
    ('LTC', 'USDTM',),
    ('UNI', 'USDTM',),
    ('LUNA', 'USDTM',),
    ('LINK', 'USDTM',),
    ('SOL', 'USDTM',),
]
TASK_PERIODS = {
    # 'kucoin_data.collect.spot_orders': 2,
    'kucoin_data.collect.spot_trades': 4,
    # 'kucoin_data.collect.futures_orders': 2,
    'kucoin_data.collect.futures_trades': 4,
    'kucoin_data.store.orders_and_trades': 1,
}
