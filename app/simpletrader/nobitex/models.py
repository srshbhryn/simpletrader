from django.db import models

from simpletrader.kucoin.models import Asset


class Market(models.Model):
    base_asset = models.IntegerField(choices=Asset.choices)
    quote_asset = models.IntegerField(choices=Asset.choices)

    @property
    def symbol(self):
        return Asset._value2member_map_[self.base_asset].name.upper() + \
            Asset._value2member_map_[self.quote_asset].name.upper()

    def __str__(self):
        return self.symbol

