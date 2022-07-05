
from django.core.management.base import BaseCommand

from simpletrader.base.models import Exchange
from simpletrader.kucoin.models import Asset, SpotMarket, FuturesContract, Market

class Command(BaseCommand):

    def handle(self, *args, **options):
            self._reinit_markets()

    def _reinit_markets(self):
        self.stdout.write(self.style.WARNING('Reiniting Spot Markets...'))
        quote_asset = Asset.usdt
        base_assets = [
            asset
            for asset in Asset
            if not asset == Asset.usdt
        ]
        for base_asset in base_assets:
            market, is_created = SpotMarket.objects.get_or_create(
                base_asset=base_asset,
                quote_asset=quote_asset,
            )
            if is_created:
                self.stdout.write(f'Added Spot Market \'{market.symbol}\'.')
            else:
                self.stdout.write(f'Spot Market\'{market.symbol}\' already exists.')
        self.stdout.write(self.style.SUCCESS('Reiniting Spot Markets: DONE'))
        self.stdout.write(self.style.WARNING('Reiniting Futures Contracts...'))
        for base_asset in base_assets:
            market, is_created = FuturesContract.objects.get_or_create(
                base_asset=base_asset,
                quote_asset=quote_asset,
            )
            if is_created:
                self.stdout.write(f'Added Futures Contract\'{market.symbol}\'.')
            else:
                self.stdout.write(f'Futures Contract\'{market.symbol}\' already exists.')
        self.stdout.write(self.style.SUCCESS('Reiniting Futures Contracts: DONE'))
        self.stdout.write(self.style.WARNING('Creating generic markets...'))
        for market_id in SpotMarket.objects.all().values_list('id', flat=True):
            _, _ = Market.objects.get_or_create(related_id=market_id, type=Exchange.kucoin_spot)
        for market_id in FuturesContract.objects.all().values_list('id', flat=True):
            _, _ = Market.objects.get_or_create(related_id=market_id, type=Exchange.kucoin_futures)
        self.stdout.write(self.style.SUCCESS('Creating generic markets: DONE'))