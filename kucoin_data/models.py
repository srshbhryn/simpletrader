from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField

class Asset(models.Model):
    spot_name = models.CharField(unique=True, max_length=8)
    futures_name = models.CharField(unique=True, max_length=8, blank=True, null=True)

    def delete(self):
        pass


class SpotMarketManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('base_asset', 'quote_asset')


class SpotMarket(models.Model):
    base_asset = models.ForeignKey(Asset, related_name='+', on_delete=models.CASCADE)
    quote_asset = models.ForeignKey(Asset, related_name='+', on_delete=models.CASCADE)
    base_min_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    quote_min_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    base_increment = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    quote_increment = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    price_increment = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)

    objects = SpotMarketManager()

    @property
    def symbol(self):
        return self.base_asset.spot_name + '-' + self.quote_asset.spot_name


class FuturesContractManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('base_asset', 'quote_asset')


class FuturesContract(models.Model):
    base_asset = models.ForeignKey(Asset, related_name='+',  on_delete=models.CASCADE)
    quote_asset = models.ForeignKey(Asset, related_name='+',  on_delete=models.CASCADE)
    lot_multiplier = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    lot_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    tick_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    index_price_tick_size = models.DecimalField(max_digits=32, decimal_places=16, null=True, default=None)
    max_leverage = models.IntegerField(null=True, default=None)

    objects = FuturesContractManager()

    @property
    def symbol(self):
        return self.base_asset.futures_name + self.quote_asset.futures_name


class SpotOrderBook(models.Model):
    market = models.ForeignKey(SpotMarket, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='1 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_bid = models.BooleanField()


class SpotTrade(models.Model):
    market = models.ForeignKey(SpotMarket, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='4 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_buyer_maker = models.BooleanField()


class FuturesOrderBook(models.Model):
    market = models.ForeignKey(FuturesContract, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='1 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_bid = models.BooleanField()


class FuturesTrade(models.Model):
    market = models.ForeignKey(FuturesContract, on_delete=models.CASCADE)
    time = TimescaleDateTimeField(interval='4 hour')
    price = models.FloatField()
    volume = models.FloatField()
    is_buyer_maker = models.BooleanField()
