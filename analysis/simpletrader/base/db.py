from django.db.models import Func, IntegerField


class Round(Func):
    function = 'ROUND'
    name = 'round'
    template='%(function)s(%(expressions)s)'
    output_field = IntegerField()

