import json
import decimal

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
    if order['price']:
        order['price'] = decimal.Decimal(order['price'])
    order['volume'] = decimal.Decimal(order['volume'])
    client = bot.get_client(exchange_id)
    order = client.place_order(order)
    order_object = Order.objects.create(**{
        **order,
        'placed_by': bot,
        'account': bot.account(exchange_id),
    })
    return json.dumps({'code': 0, 'id': order_object.id})


@shared_task(name='trader.cancel_order',)
def cancel_order_task(args):
    args = json.loads(args)
    bot_token = args['bot_token']
    order_id = args['order_id']
    order: Order = Order.objects.get(pk=order_id)
    bot: Bot = Bot.get(bot_token)
    client = bot.get_client(order.exchange_id)
    client.cancel_order(order.external_id)
    status_name = 'canceled_partially_filled' if Fill.objects.filter(
        external_order_id=order.external_id,
        external_id=order.external_id
    ).exists() else 'canceled_no_fill'
    order.status_id = OrderState.get_by('name', status_name).id
    order.save(update_fields=['status_id',])
    return json.dumps({'code': 0})


@shared_task(name='trader.get_order_status',)
def get_order_status_task(args):
    args = json.loads(args)
    order_id = args['order_id']
    order: Order = Order.objects.filter(id=order_id).only('status_id').first()
    filled_volume = Fill.objects.filter(
        external_order_id=order.external_id,
        exchange_id=order.exchange_id
    ).aggregate(fv=models.Sum('volume')).get('fv') or decimal.Decimal('0')
    filled_volume = float(filled_volume)
    return json.dumps({'code': 0, 'status_id': order.status_id, 'filled_volume': filled_volume})


@shared_task(name='trader.get_balance',)
def get_balance_task(args):
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
        'free_balance': float(last_record.free_balance),
        'blocked_balance': float(last_record.blocked_balance),
    })


@shared_task(name='trader._update_order_status',)
def update_order_status_task(exchange_id, external_order_id):
    order = Order.objects.get(external_id=external_order_id, exchange_id=exchange_id)
    filled_volume = Fill.objects.filter(
        external_order_id=external_order_id,
        exchange_id=exchange_id
    ).aggregate(fv=models.Sum('volume')).get('fv') or decimal.Decimal('0')
    if abs(order.volume - filled_volume) < decimal.Decimal('0.005'):
        status_name = 'filled'
    else:
        status_name = 'open_partially_filled'
    order.status_id = OrderState.get_by('name', status_name).id
    order.save(update_fields=['status_id',])
    return None
