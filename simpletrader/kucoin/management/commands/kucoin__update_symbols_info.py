from decimal import Decimal

from django.core.management.base import BaseCommand

from simpletrader.kucoin.models import SpotMarket, FuturesContract
from simpletrader.kucoin.clients import get_futures_client, get_spot_client

class Command(BaseCommand):

    def handle(self, *args, **options):
        self._update_spot_symbols_info()
        self._update_futures_contracts_info()

    def _update_spot_symbols_info(self):
        self.stdout.write(self.style.WARNING('Updating Spot Markets...'))
        client = get_spot_client()
        symbols = client.get_symbol_list()
        def get_symbol(sym):
            return next(
                (symbol for symbol in symbols if symbol['symbol'] == sym),
                None,
            )
        markets = SpotMarket.objects.all()
        for market in markets:
            symbol = get_symbol(market.symbol)
            if symbol is None:
                self.stderr.write(
                    self.style.ERROR(f'Could not find symbol {market.symbol}.')
                )
            else:
                market.base_min_size = Decimal(symbol['baseMinSize'])
                market.quote_min_size = Decimal(symbol['quoteMinSize'])
                market.base_increment = Decimal(symbol['baseIncrement'])
                market.quote_increment = Decimal(symbol['quoteIncrement'])
                market.price_increment = Decimal(symbol['priceIncrement'])
                market.save()
                self.stdout.write(
                    f'updated market info for \'{market.symbol}\' successfully.'
                )
        self.stdout.write(self.style.SUCCESS('Updating Spot Markets: DONE.'))

    def _update_futures_contracts_info(self):
        self.stdout.write(self.style.WARNING('Updating Futures Contracts...'))
        client = get_futures_client()
        symbols = client.get_contracts_list()
        def get_symbol(sym):
            return next(
                (symbol for symbol in symbols if symbol['symbol'] == sym),
                None,
            )
        contracts = FuturesContract.objects.all()
        for contract in contracts:
            symbol = get_symbol(contract.symbol)
            if symbol is None:
                self.stderr.write(
                    self.style.ERROR(f'Could not find contract {contract.symbol}.')
                )
            else:

                contract.lot_multiplier = Decimal(symbol['multiplier'])
                contract.lot_size = Decimal(symbol['lotSize'])
                contract.tick_size = Decimal(symbol['tickSize'])
                contract.index_price_tick_size = Decimal(symbol['indexPriceTickSize'])
                contract.max_leverage = Decimal(symbol['maxLeverage'])
                contract.save()
                self.stdout.write(
                    f'updated contract info for \'{contract.symbol}\' successfully.'
                )
        self.stdout.write(self.style.SUCCESS('Updating Futures Markets: DONE.'))
