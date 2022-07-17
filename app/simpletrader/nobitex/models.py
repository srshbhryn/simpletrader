from django.db import models


class Market(models.Model):
    base_asset = models.CharField(max_length=8)
    quote_asset = models.CharField(max_length=8)

    @property
    def symbol(self):
        return self.base_asset + self.quote_asset

    def __str__(self):
        return self.symbol

