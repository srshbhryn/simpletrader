
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q


from simpletrader.kucoin.models import Asset, Market, Exchange
from simpletrader.nobitex.models import Market as NbxMarket
from simpletrader.nobitex import configs

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for base_asset, quote_asset in configs.MARKETS:
            NbxMarket.objects.get_or_create(
                base_asset=base_asset,
                quote_asset=quote_asset,
            )
            for nbx_market_id in NbxMarket.objects.values_list('id', flat=True):
                Market.objects.get_or_create(
                    type=Exchange.nobitex,
                    related_id=nbx_market_id
                )


