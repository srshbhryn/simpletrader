from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

from simpletrader.base.models import Exchange

class Asset(models.IntegerChoices):
    irt = -1
    usdt = 0
    btc = 1
    eth = 2
    ltc = 3
    xrp = 4
    bch = 5
    bnb = 6
    eos = 7
    xlm = 8
    etc = 9
    trx = 10
    doge = 11
    uni = 12
    link = 13
    dot = 14
    aave = 15
    ada = 16
    shib = 17
    ftm = 18
    matic = 19
    axs = 20
    mana = 21
    sand = 22

    @classmethod
    def spot_symbol(cls, asset):
        if isinstance(asset, int):
            asset = Asset(asset)
        return asset.label.upper()

    @classmethod
    def futures_symbol(cls, asset):
        if isinstance(asset, int):
            asset = Asset(asset)
        if asset.value == Asset.usdt:
            return 'USDTM'
        if asset.value == Asset.btc:
            return 'XBT'
        return Asset.spot_symbol(asset)


class SpotMarket(models.Model):
    base_asset = models.IntegerField(choices=Asset.choices)
    quote_asset = models.IntegerField(choices=Asset.choices)
    base_min_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    quote_min_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    base_increment = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    quote_increment = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    price_increment = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)

    @property
    def symbol(self):
        return Asset.spot_symbol(self.base_asset) + '-' + Asset.spot_symbol(self.quote_asset)


class FuturesContract(models.Model):
    base_asset = models.IntegerField(choices=Asset.choices)
    quote_asset = models.IntegerField(choices=Asset.choices)
    lot_multiplier = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    lot_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    tick_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    index_price_tick_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    max_leverage = models.IntegerField(null=True, default=None)

    @property
    def symbol(self):
        return Asset.futures_symbol(self.base_asset) + Asset.futures_symbol(self.quote_asset)


class Market(models.Model):
    type = models.IntegerField(choices=Exchange.choices)
    related_id = models.IntegerField()

class Trade(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='24 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_buyer_maker = models.BooleanField()

    objects = TimescaleManager()
