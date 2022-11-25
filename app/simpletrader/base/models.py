from django.db import models
from django.db.models import Q

class Country(models.IntegerChoices):
    USA = 1
    GERMANY = 2
    UK = 3
    FRANCE = 4
    CHINA = 5
    INDIA = 6


class Exchange(models.IntegerChoices):
    nobitex = 1
    kucoin_spot = 2
    kucoin_futures = 3


def assuming(condition: Q, then: Q) -> Q:
    '''A => B is equivalent to B or not A
    '''
    return Q(~Q(condition) | Q(then))
