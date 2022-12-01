
from simpletrader.trader.sharedconfigs import Exchange

from .nobitex import Nobitex
from .kucoin_spot import KucoinSpot
from .kucoin_futures import KucoinFutures
from .dummy import Dummy


def get_client(exchange_id, bot):
    from simpletrader.trader.models import Bot
    from simpletrader.trader_god.models import BotStateChange
    bot_token = bot.token
    is_fake = lambda: not (
        BotStateChange.get_bot_state(
            bot,
        ) == BotStateChange.States.real_running
    )
    account = Bot.get(bot_token).account(exchange_id, is_fake)
    client = Dummy if bot.is_managed and is_fake() else (
        {
            Exchange.get_by('name', 'nobitex').id: Nobitex,
            Exchange.get_by('name', 'kucoin_spot').id: KucoinSpot,
            Exchange.get_by('name', 'kucoin_futures').id: KucoinFutures,
        }[exchange_id]
    )(account.credentials, bot_token)
    client.account_id = account.id
    client.exchange_id = exchange_id
    return client
