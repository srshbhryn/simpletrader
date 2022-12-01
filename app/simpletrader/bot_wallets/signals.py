import decimal

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from simpletrader.trader.sharedconfigs import Market, OrderState
from simpletrader.trader.models import Order, Fill
from simpletrader.trader.utils import final_order_state_ids, open_order_state_ids

from .models import _WalletTransactionTypes
from .manager import get_wallet_manager


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance: Order, created, update_fields, **kwargs):
    if instance.status_id in open_order_state_ids() + [OrderState.get_by('name', 'filled').id]:
        return
    if instance.org_status_id in final_order_state_ids():
        return
    if instance.org_status_id == instance.status_id:
        return
    market: Market = Market.get_by('id', instance.market_id)
    no_fill_end = instance.status_id in [
        'failed_no_fill'
        'canceled_no_fill'
    ]
    asset_id = (
        market.base_asset.id
        if instance.is_sell else
        market.quote_asset.id
    )
    volume = (
        instance.volume
        if instance.is_sell else
        (instance.volume * instance.price)
    )
    if created:
        get_wallet_manager(instance.account.bot).create_transaction(
            asset_id=asset_id,
            amount=volume,
            type=_WalletTransactionTypes.block,
        )
        return
    if no_fill_end:
        get_wallet_manager(instance.account.bot).create_transaction(
            asset_id=asset_id,
            amount=-volume,
            type=_WalletTransactionTypes.block,
        )
        return
    asset_id = (
        market.base_asset.id
        if instance.is_sell else
        market.quote_asset.id
    )
    blocked_volume = volume - Fill.objects.filter(
        external_order_id=instance.external_id,
        exchange_id=instance.exchange_id
    ).aggregate(
        fv=models.Sum('volume')
        if instance.is_sell else
        models.Sum(models.F('volume') * models.F('price'))
    ).get('fv') or decimal.Decimal('0')
    get_wallet_manager(instance.account.bot).create_transaction(
        asset_id=asset_id,
        amount=-blocked_volume,
        type=_WalletTransactionTypes.block,
    )


@receiver(pre_save, sender=Fill)
def fill_pre_save(sender, instance: Fill, created, update_fields, **kwargs):
    if not created:
        return
    market: Market = Market.get_by('id', instance.market_id)
    asset_id_to_value_map = {
        asset_id: decimal.Decimal('0')
        for asset_id in {
            market.base_asset.id,
            market.quote_asset.id,
            instance.fee_asset_id,
        }
    }
    asset_id_to_value_map[instance.fee_asset_id] += -instance.fee
    asset_id_to_value_map[instance.market.base_asset.id] += (
        -instance.volume
        if instance.is_sell else
        instance.volume
    )
    asset_id_to_value_map[instance.market.quote_asset.id] += (
        (instance.volume * instance.price)
        if instance.is_sell else
        -(instance.volume * instance.price)
    )
    for asset_id, volume in asset_id_to_value_map.items():
        get_wallet_manager(instance.account.bot).create_transaction(
            asset_id=asset_id,
            amount=volume,
            type=(
                _WalletTransactionTypes.gain
                if volume > 0 else
                _WalletTransactionTypes.pay
            ),
        )
