from django.shortcuts import HttpResponse

from .tasks import collect_market_data
from .models import Market
# from .client import Client


def test_celery(request):
    # client = Client()
    # print(client.get_orderbook('BTCIRT'))

    # return HttpResponse(
    #     str(client.get_orderbook('BTCIRT'))
    # )
    t = collect_market_data.delay()
    # collect_market_data.delay(market.symbol, market.id)
    return HttpResponse(':D')