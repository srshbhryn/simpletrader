from django.db.models import Func


class Round(Func):
    function = 'ROUND'
    name = 'round'
    template='%(function)s(%(expressions)s)'

