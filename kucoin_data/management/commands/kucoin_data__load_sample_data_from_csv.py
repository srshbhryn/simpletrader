import decimal
import datetime

from django.core.management.base import BaseCommand

from kucoin_data.models import SpotTrade, FuturesTrade

def time_serializer(time_str):
    time_str = time_str.split('-')
    temp = time_str[-2]
    temp = temp.split('.')
    if len(temp) == 1:
        temp += ['000000']
    temp[-1] += '0' * (6 - len(temp[-1]))
    temp = '.'.join(temp)
    time_str[-2] = temp
    if len(time_str[-1]) == 2:
        time_str[-1] += '00'
    time_str = '-'.join(time_str)
    return datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f%z')


def line_to_trade(line):
    keys = ['pk', 'time', 'price', 'volume', 'is_buyer_maker', 'market_id']
    serializeres = {
        'pk': int,
        'time': time_serializer,
        'price': decimal.Decimal,
        'volume': decimal.Decimal,
        'is_buyer_maker': lambda value: value == 't',
        'market_id': int,
    }
    raw_values = line.split(',')
    return {
        k: serializeres[k](v)
        for k, v in zip(keys, raw_values)
    }


class Command(BaseCommand):

    def add_arguments(self , parser):
        parser.add_argument(
            '--filepath',
            default=None,
        )
        parser.add_argument(
            '--model',
            default=None,
            choices=['spottrades', 'futurestrades'],
        )

    def handle(self, *args, **options):
        filepath = options['filepath']
        model = options['model']
        if model == 'spottrades':
            self._store_trades(filepath, SpotTrade)
        if model == 'futurestrades':
            self._store_trades(filepath, FuturesTrade)

    def _store_trades(self, filepath, model_class):
        with open(filepath, 'r') as f:
            lines = f.readlines()[1:]
        objects = [
            model_class(**line_to_trade(line[:-1]))
            for line in lines
        ]
        while len(objects) > 1000:
            model_class.objects.bulk_create(
                objects[:1000]
            )
            objects = objects[1000:]
        model_class.objects.bulk_create(
            objects
        )
