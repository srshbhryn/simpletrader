
from celery import shared_task

from simpletrader.trade.services import place_order, cancel_order, get_order_status, get_balance


@shared_task(name='trade.place_order')
def place_order_task(account_uuid, pair_id, leverage, volume, is_sell, price, client_order_id,):
    client_order_id = client_order_id or None
    leverage = leverage
    volume = volume
    is_sell = is_sell == 'true'
    return place_order(account_uuid, client_order_id, pair_id, leverage, price, volume, is_sell,)


@shared_task(name='trade.cancel_order')
def cancel_order_task(order_uid):
    return cancel_order(order_uid)


@shared_task(name='trade.get_order_status')
def get_order_status_task(order_uid):
    return get_order_status(order_uid)


@shared_task(name='trade.get_balance')
def get_balance_task(account_uid, asset_id):
    return get_balance(account_uid, asset_id)
