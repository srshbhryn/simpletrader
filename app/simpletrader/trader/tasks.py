import json

from celery import shared_task

from .models import Bot, Order
from .clients.base import OrderParams


@shared_task(name='trader.place_order',)
def place_order_task(args):
    order: OrderParams = json.loads(args)
    bot_token = order['bot_token']
    exchange_id = order['exchange_id']
    del order['bot_token']
    del order['exchange_id']
    bot: Bot  = Bot.objects.get(token=bot_token)
    client = bot.get_client(exchange_id)
    order = client.place_order(order)
    Order.objects.create({
        **order,
        'placed_by': bot,
        'account': bot.botaccount_set.filter(account__exchange_id=exchange_id).first(),
    })
    return json.dumps(order)


@shared_task(name='trader.get_order_status',)
def get_order_status_task(*args):
    a, b = args[0]
    return async_to_sync(main)(a, b)


@shared_task(name='trader.cancel_order',)
def cancel_order_task(*args):
    a, b = args[0]
    return async_to_sync(main)(a, b)
