import asyncio
import json
import time
# from django.as
from celery import shared_task

from asgiref.sync import async_to_sync


from simpletrader.trader.models import Bot

class Client:
    def __init__(self) -> None:
        self._a = 0

    @property
    def a(self):
        self._a += 1
        return self._a

client = Client()

async def job0(a):
    await asyncio.sleep(.5)
    return a
async def job1(b):
    await asyncio.sleep(.5)
    return b

async def main(a, b):
    sum = 0
    for value in asyncio.as_completed([
        job0(a),
        job1(b),
    ]):
        sum += await value
    return sum + client.a

@shared_task(name='trader.test_task',)
def test_task(*args):
    a, b = args[0]
    return async_to_sync(main)(a, b)

async def place_order():
    pass

@shared_task(name='trader.place_order',)
def place_order_task(args):
    data = json.loads(args)
    bot_token = data['bot_token']
    market_id = data['market_id']
    amount = data['amount']
    amount = data['amount']
    return async_to_sync(place_order)(a, b)

@shared_task(name='trader.get_order_status',)
def get_order_status_task(*args):
    a, b = args[0]
    return async_to_sync(main)(a, b)

@shared_task(name='trader.cancel_order',)
def cancel_order_task(*args):
    a, b = args[0]
    return async_to_sync(main)(a, b)

