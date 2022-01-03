# simpletrader


celery -A simpletrader worker -l DEBUG -Q celery,high --pool=gevent --concurrency=100 --queues=api_call
celery -A simpletrader worker -l DEBUG -Q celery,high  --concurrency=3 --queues=db_insert

celery -A simpletrader beat -l INFO --scheduler=django_celery_beat.schedulers:DatabaseScheduler

