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
