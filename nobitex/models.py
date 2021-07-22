from django.db import models

class Market(models.Model):
    asset_name = models.CharField(max_length=6)
    currency_name = models.CharField(max_length=6)

    @property
    def symbol(self):
        return self.asset_name+self.currency_name

    def __str__(self):
        return self.symbol


class MarketData(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    volume = models.FloatField()
    is_buy =models.BooleanField()

    # def __str__(self):
    #     return f'{self.market.symbol} {self.created_at} {"Buy" if self.is_buy else "Sell"} {self.volume}@{self.price}'
    def __str__(self):
        return f'{self.market.symbol} {self.created_at}'


class MarketTrades(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    time = models.IntegerField()
    price = models.FloatField()
    volume = models.FloatField()
    is_buy =models.BooleanField()

    def __str__(self):
        return f'{self.market.symbol} {self.created_at}'
