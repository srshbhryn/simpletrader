import logging
import datetime

from celery import shared_task

from django.db.models import Max
from django.utils import timezone

from simpletrader.base.utils import locked_proccess
from simpletrader.indices.config import Type
from simpletrader.kucoin.models import SpotTrade, FuturesTrade
from simpletrader.indices.models import Measure, Measurement

log = logging.getLogger('django')


class FireRecent:
    def __init__(self, measure_type):
        self.measures = Measure.objects.filter(type=measure_type)

    def run(self):
        log.info('started')
        for measure in self.measures:
            try:
                self.index_manager(measure)
            except Exception as e:
                log.error(f'{e}')
        log.info('ended')

    get_latest_data_map = {
        Type.spot_trade_entropy: lambda related_id: SpotTrade.objects.filter(
            market_id=related_id).aggregate(max_time=Max('time')).get('max_time'),
        Type.futures_trade_entropy: lambda related_id: FuturesTrade.objects.filter(
            market_id=related_id).aggregate(max_time=Max('time')).get('max_time'),
        Type.spot_candle: lambda related_id: SpotTrade.objects.filter(
            market_id=related_id).aggregate(max_time=Max('time')).get('max_time'),
        Type.futures_candle: lambda related_id: FuturesTrade.objects.filter(
            market_id=related_id).aggregate(max_time=Max('time')).get('max_time'),
    }

    def index_manager(self, measure):
        period = measure.period
        def get_latest_data():
            return self.get_latest_data_map[measure.type](measure.related_id)

        def get_latest_measurement():
            return measure.measurement_set.all().aggregate(max_time=Max('time')).get('max_time', 0)

        max_measure_time = get_latest_measurement()
        if max_measure_time is None:
            first_measure_time = timezone.make_aware(datetime.datetime.fromtimestamp(0)) + int((
                get_latest_data() - timezone.make_aware(datetime.datetime.fromtimestamp(0))
            ) / period) * period
            Measurement(
                measure=measure,
                time=first_measure_time,
            ).run_task(is_high_priority=True)
            return
        next_measure_time = max_measure_time + period / 2
        max_data_time = get_latest_data()
        if next_measure_time <= max_data_time:
            Measurement(
                measure=measure,
                time=next_measure_time,
            ).run_task(is_high_priority=True)



@shared_task(name='kucoin_index.manage.fire_recent', ignore_result=True, store_errors_even_if_ignored=True)
@locked_proccess
def fire_recent(measure_type):
    manager = FireRecent(measure_type)
    manager.run()
