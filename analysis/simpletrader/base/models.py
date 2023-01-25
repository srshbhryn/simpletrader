from django.db.models import Q


def assuming(condition: Q, then: Q) -> Q:
    '''A => B is equivalent to B or not A
    '''
    return ~condition | then
