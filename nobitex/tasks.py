from celery import shared_task
import time

@shared_task()
def test_task(a):
    # print('salam')
    time.sleep(4)
    print('bye')
    return {'asd':123, 'zxc':'asd', 'qwew':True}

