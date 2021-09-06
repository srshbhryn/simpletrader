import time

from django.db.models import Min, Max

from nobitex.models import Market, MarketTrades


markets = Market.objects.all()

def test_interpolation(market):
    trades = MarketTrades.objects.filter(market=market)
    query = trades.annotate(
        min_time=Min('time'),
        max_time=Max('time'),
    )
    min_time = query()

