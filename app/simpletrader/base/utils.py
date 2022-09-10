import datetime
import logging
import time
import json

from django.core.cache import cache
from django.utils.timezone import make_aware


log = logging.getLogger('django')

def unix_timestamp_to_datetime(unix_timestamp):
    return make_aware(datetime.datetime.fromtimestamp(unix_timestamp))

def unix_timestamp_ms_to_datetime(unix_timestamp):
    return make_aware(datetime.datetime.fromtimestamp(unix_timestamp / 1000))

class ProccessLock:
    def __init__(self, key):
        self.key = key

    def lock(self):
        timestamp = time.time()
        cached_timestamp = cache.get_or_set(self.key, timestamp)
        return timestamp == cached_timestamp

    def unlock(self):
        cache.delete(self.key)

def locked_proccess(func):
    def inner(*args, **kwargs):
        lock = ProccessLock('pl'+func.__name__+json.dumps({
            'a': args,
            'k': kwargs,
        }))
        if not lock.lock():
            return 'locked'
        result = None
        try:
            result = func(*args, **kwargs)
        finally:
            lock.unlock()
        return result
    return inner


class LimitGuard:
    def __init__(self, rate='10/m', key=None):
        self.key = key
        self.key_value = None
        self._rate_count, self._rate_period = self._translate_rate(rate)
        if key is not None:
            self._call_times_map = {}
        else:
            self._call_times = []

    def _translate_rate(self, rate):
        count, period = rate.split('/')
        count = int(count)
        period_value = float(period[:-1] or 1)
        period_unit = period[-1]
        period_unit = {
            's': 1,
            'm': 60,
            'h': 3600,
        }[period_unit]
        period = period_unit * period_value
        return count, period

    def _get_last_period_call_count(self):
        nw = time.time()
        self._call_times = [
            ts for ts in self._call_times
            if nw - ts <= self._rate_period
        ]
        return len(self._call_times)

    def _get_keyed_last_period_call_count(self, key):
        nw = time.time()
        call_times = self._call_times_map.get(key) or []
        self._call_times_map[key] = [
            ts for ts in call_times
            if nw - ts <= self._rate_period
        ]
        return len(self._call_times_map[key])

    @property
    def _last_period_call_count(self):
        if self.key is None:
            return self._get_last_period_call_count()
        return self._get_keyed_last_period_call_count(self.key_value)

    def __call__(self, fn):
        def inner(*args, **kwargs):
            if self.key is not None:
                self.key_value = kwargs.get(self.key)
            while self._last_period_call_count >= self._rate_count:
                wait_time = self._rate_period - (time.time() - self._call_times[0])
                log.info(f'LimitGuard\t{fn.__name__}\twaiting for {wait_time:.4}s.')
                time.sleep(
                    wait_time
                     + 0.05
                )
                log.info(f'LimitGuard\t{fn.__name__}\tgo.')

            self._call_times.append(time.time())
            result = fn(*args, **kwargs)
            return result
        return inner
