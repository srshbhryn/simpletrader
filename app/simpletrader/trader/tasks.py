import json

from django.db import models
from celery import shared_task


from .sharedconfigs import OrderState
from .models import (
    Bot,
    Order,
    Account,
    WalletSnapShot,
    Fill
)
from .clients.base import OrderParams


@shared_task(name='trader.place_order',)
def place_order_task(args):
    order: OrderParams = json.loads(args)
    bot_token = order['bot_token']
    exchange_id = order['exchange_id']
    del order['bot_token']
    del order['exchange_id']
    bot: Bot  = Bot.get(bot_token)
    client = bot.get_client(exchange_id)
    order = client.place_order(order)
    Order.objects.create({
        **order,
        'placed_by': bot,
        'account': bot.account,
    })
    # return json.dumps(order)
    return json.dumps({'code': 0})


@shared_task(name='trader.cancel_order',)
def cancel_order_task(args):
    args = json.loads(args)
    bot_token = args['bot_token']
    exchange_id = args['exchange_id']
    order_id = args['exchange_id']
    bot: Bot  = Bot.get(bot_token)
    client = bot.get_client(exchange_id)
    client.cancel_order(order_id)
    Order.objects.filter(exchange_id=order_id).update(
        status_id=OrderState.get_by('name', 'cancelled').id
    )
    return json.dumps({'code': 0})


@shared_task(name='trader.get_order_status',)
def get_order_status_task(args):
    args = json.loads(args)
    bot_token = args['bot_token']
    exchange_id = args['exchange_id']
    order_id = args['exchange_id']
    order: Order = Order.objects.get(exchange_id=order_id)
    if order.status_id in Order.FINAL_STATE_IDS:
        return json.dumps({'code': 0, 'status_id': order.status_id})

    # FINAL_STATE_IDS

# @shared_task(name='trader.cancel_order',)
# def cancel_order_task(*args):
#     a, b = args[0]
#     return async_to_sync(main)(a, b)


@shared_task(name='trader.cancel_order',)
def get_balance(args):
    args = json.loads(args)
    bot_token = args['bot_token']
    exchange_id = args['exchange_id']
    asset_id = args['asset_id']
    account: Account  = Bot.get(bot_token).account(exchange_id)
    last_record = WalletSnapShot.objects.filter(
        account=account,
        asset_id=asset_id,
    ).order_by('timestamp').last()
    if last_record is None:
        return json.dumps({'code': 4})
    return json.dumps({
        'code': 0,
        'timestamp': last_record.timestamp.isoformat(),
        'free_balance': last_record.free_balance,
        'blocked_balance': last_record.blocked_balance,
    })


@shared_task(name='trader.cancel_order',)
def get_fills(args):
    args = json.loads(args)
    order_id = args['order_id']
    fills = Fill.objects.filter(
        external_order_id=Order.get(id=order_id).external_id
    ).aggregate(fills=models.Sum('amount')).get('fills') or 0
    return json.dumps({
        'code': 0,
        'fills': fills,
    })
