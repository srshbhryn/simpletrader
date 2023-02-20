
from celery import shared_task

from simpletrader.base.serializers import serialize
from simpletrader.trade.services import place_order, cancel_order, get_order_status, get_balance


@shared_task(name='trade.place_order')
def place_order_task(account_uuid, pair_id, leverage, volume, is_sell, price, client_order_id,):
    client_order_id = client_order_id or None
    leverage = leverage
    volume = volume
    is_sell = is_sell == 'true'
    return serialize(place_order(
        account_uuid=account_uuid,
        client_order_id=client_order_id,
        pair_id=pair_id,
        leverage=leverage,
        price=price,
        volume=volume,
        is_sell=is_sell,
    ))


@shared_task(name='trade.cancel_order')
def cancel_order_task(order_uid):
    return serialize(cancel_order(order_uid))


@shared_task(name='trade.get_order_status')
def get_order_status_task(order_uid):
    return serialize(get_order_status(order_uid))


@shared_task(name='trade.get_balance')
def get_balance_task(account_uid, asset_id):
    return serialize(get_balance(account_uid, asset_id))
