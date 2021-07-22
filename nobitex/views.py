from django.shortcuts import HttpResponse

from .tasks import test_task

def test_celery(request):
    print('aaaaaaaaaaa')
    t0 = test_task.delay(None)
    print(t0.ready())
    print('bbbbbbbbbbb')

    return HttpResponse(':d')
