import datetime
import time
import json

from django.core.cache import cache
from django.utils.timezone import make_aware


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
