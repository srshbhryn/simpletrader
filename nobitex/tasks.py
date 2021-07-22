from celery import shared_task

from .models import Market, MarketData, MarketTrades

@shared_task
def collect_market_data():
    markets = Market.objects.all()
    # for


@shared_task
def collect_market_trades():
    pass