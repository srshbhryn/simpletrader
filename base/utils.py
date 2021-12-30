import datetime

from django.utils.timezone import make_aware


def unix_timestamp_to_datetime(unix_timestamp):
    return make_aware(datetime.datetime.fromtimestamp(unix_timestamp))

def unix_timestamp_ms_to_datetime(unix_timestamp):
    return make_aware(datetime.datetime.fromtimestamp(unix_timestamp / 1000))
