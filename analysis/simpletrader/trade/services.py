from decimal import Decimal
from typing import Optional

from django.db import models
from django.db.transaction import atomic

from simpletrader.base.serializers import serialize
from simpletrader.analysis.models import Asset, Pair, OrderStatus
from simpletrader.accounts.models import Wallet, Account, Transaction
from simpletrader.trade.models import Order, Fill



@atomic
def place_order(
    *,
    account_uuid: str,
    client_order_id: Optional[str],
    pair_id: int,
    leverage: Optional[int],
    price: Optional[Decimal],
    volume: Decimal,
    is_sell: bool,
):
    leverage = leverage or 1
    account = Account.objects.select_related('exchange').get(uid=account_uuid)
    exchange = account.exchange
    pair = Pair.objects.select_related('base_asset', 'quote_asset').get(pk=pair_id)
    blocking_asset = pair.base_asset if is_sell else pair.quote_asset
    blocking_amount = volume if is_sell else volume * price
    Wallet.objects.get(account=account, asset=blocking_asset).create_transaction(
        tp=Transaction.Type.block, amount=blocking_amount
    )
    order = Order.objects.create(
        account=account,
        client_order_id=client_order_id,
        leverage=leverage,
        pair=pair,
        exchange=exchange,
        status=OrderStatus.objects.get(name='open'),
        price=price,
        volume=volume,
        is_sell=is_sell,
    )
    return order.uid


@atomic
def cancel_order(order_uid):
    order: Order = Order.objects.select_for_update().first(uid=order_uid)
    assert order.status == OrderStatus.objects.get(name='open')
    order.status = OrderStatus.objects.get(name='canceled')
    order.save(update_fields='status')
    return 0


def get_order_status(order_uid):
    order: Order = Order.objects.get(uid=order_uid)
    filled_volume = Fill.objects.filter(order_uid=order_uid).aggregate(
        fv=models.Sum('volume')
    ).get('fv') or Decimal('0')
    return serialize({'status_id': order.status_id, 'filled_volume': filled_volume})

def get_balance(account_uid, asset_id):
    account = Account.objects.select_related('exchange').get(uid=account_uid)
    asset = Asset.objects.get(pk=asset_id)
    wallet = Wallet.objects.get_or_create(
        account=account,
        asset=asset,
    )
    return {'blocked': wallet.blocked_balance, 'free':wallet.free_balance}
