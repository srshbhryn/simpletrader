
from simpletrader.trader.sharedconfigs import Exchange

from .nobitex import Nobitex
from .kucoin_spot import KucoinSpot
from .kucoin_futures import KucoinFutures


_clients = {}

def _create_client(exchange_id, bot_token):
    from simpletrader.trader.models import BotAccount
    client_class = {
        Exchange.get_by('name', 'nobitex').id: Nobitex,
        Exchange.get_by('name', 'kucoin_spot').id: KucoinSpot,
        Exchange.get_by('name', 'kucoin_futures').id: KucoinFutures,
    }[exchange_id]
    credentials = BotAccount.get_bot_credentials(exchange_id, bot_token)
    return client_class(bot_token, credentials)

def get_client(exchange_id, bot_token):
    client_key = (exchange_id, bot_token)
    if client_key in _clients:
        return _clients[client_key]
    client = _create_client(exchange_id, bot_token)
    _clients[client_key] = client
    return client
