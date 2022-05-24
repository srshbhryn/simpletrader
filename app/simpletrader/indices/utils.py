from math import log2

from celery import shared_task
from simpletrader.indices.config import get_task_names

from django.db.models import Func


class Round(Func):
    function = 'ROUND'
    name = 'round'
    template='%(function)s(%(expressions)s)'


class register_task(object):
    def __init__(self, task_type):
        self.task_type = task_type

    def __call__(self, task_func):
        task_names = get_task_names(self.task_type)

        @shared_task(name=task_names['hp'], ignore_result=True, store_errors_even_if_ignored=True)
        def temp(*args, **kwargs):
            task_func(*args, **kwargs)

        @shared_task(name=task_names['lp'], ignore_result=True, store_errors_even_if_ignored=True)
        def temp(*args, **kwargs):
            task_func(*args, **kwargs)
        return None


def entropy(occurrences):
    occurrences = [o for o in occurrences if o]
    if len(occurrences) <= 1:
        return 0
    occurrences_sum = sum(occurrences)
    return sum([
        o / occurrences_sum * log2(occurrences_sum / o)
        for o in occurrences
    ])
