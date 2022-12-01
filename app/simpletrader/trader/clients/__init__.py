
from simpletrader.trader.sharedconfigs import Exchange

from .nobitex import Nobitex
from .kucoin_spot import KucoinSpot
from .kucoin_futures import KucoinFutures
from .dummy import Dummy


def get_client(exchange_id, bot):
    from simpletrader.trader.models import Bot
    from simpletrader.trader_god.models import BotStateChange
    bot_token = bot.token
    account = Bot.get(bot_token).account(exchange_id)
    client = Dummy if account.is_fake else (
        {
            Exchange.get_by('name', 'nobitex').id: Nobitex,
            Exchange.get_by('name', 'kucoin_spot').id: KucoinSpot,
            Exchange.get_by('name', 'kucoin_futures').id: KucoinFutures,
        }[exchange_id]
    )(account.credentials, bot_token)
    client.account_id = account.id
    client.exchange_id = exchange_id
    return client
