import logging
import time
import datetime
import multiprocessing

import django

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max, Min
from django.conf import settings
from django.utils import timezone

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from kucoin_index.config import Type, periods_map, params_map, related_ids_map
from kucoin_data.models import SpotTrade, FuturesTrade
from kucoin_index.models import Measure, Measurement

log = logging.getLogger('django')


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info('started')
        measures = Measure.objects.all()
        while True:
            for measure in measures:
                try:
                    self.index_manager(measure)
                except Exception as e:
                    log.error(f'{e}')
            log.info('sleep')
            time.sleep(10)
            log.info('woke up')


    get_latest_data_map = {
        Type.spot_trade_entropy: lambda related_id: SpotTrade.objects.filter(
            market_id=related_id).aggregate(max_time=Max('time')).get('max_time'),
        Type.futures_trade_entropy: lambda related_id: FuturesTrade.objects.filter(
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
