from decimal import Decimal
from typing import Optional

from django.db import models
from django.db.transaction import atomic

from simpletrader.base.rpc.bookwatch import get_book
from simpletrader.analysis.models import Asset, Pair, OrderStatus, Market, Exchange
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
    if price is None:
        market = Market.objects.get(exchange=exchange,pair=pair,)
        book = get_book(market.id)
        if is_sell:
            price = book.best_bid_price * .99
        else:
            price = book.best_ask_price * 1.01

    blocking_asset = pair.base_asset if is_sell else pair.quote_asset
    blocking_amount = volume if is_sell else volume * price
    Wallet.objects.get(account_uid=account.uid, asset=blocking_asset).create_transaction(
        type=Transaction.Type.block, amount=blocking_amount
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
    return {'status_id': order.status_id, 'filled_volume': filled_volume}


def get_balance(account_uid, asset_id):
    account = Account.objects.get(uid=account_uid)
    wallet = account.get_wallet(asset_id)
    return {'blocked': wallet.blocked_balance, 'free':wallet.free_balance}


def create_demo_account(exchange_id):
    account = Account.objects.create(exchange_id=exchange_id)
    wallet = account.get_wallet(Asset.objects.get(name='usdt').id)
    wallet.free_balance = Decimal('1_000')
    wallet.save()
    return account.uid
