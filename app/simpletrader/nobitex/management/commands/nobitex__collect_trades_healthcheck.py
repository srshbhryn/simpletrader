import sys
import os
from datetime import timedelta
import logging

from django.core.management.base import BaseCommand
from django.db.models import Max
from django.utils.timezone import now

from simpletrader.base.models import Exchange
from simpletrader.kucoin.models import Asset, Trade, Market
from simpletrader.nobitex.models import Market as NbxMarket

logger = logging.getLogger('django')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        usdtrls_market_id = NbxMarket.objects.get(
            base_asset=Asset.usdt,
            quote_asset=Asset.irt,
        ).id
        market_id = Market.objects.get(
            related_id=usdtrls_market_id,
            type=Exchange.nobitex).id
        max_trade_time = Trade.objects.filter(
            market_id=market_id
        ).aggregate(max_trade_time=Max('time'))['max_trade_time']
        logger.info(now() - max_trade_time)
        if now() - max_trade_time > timedelta(seconds=60):
            sys.exit(1)
        sys.exit(0)
