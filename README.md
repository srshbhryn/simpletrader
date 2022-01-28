# simpletrader


celery -A simpletrader worker -n wrk_api@%%h -l DEBUG --pool=gevent --concurrency=100 --queues=api_call
celery -A simpletrader worker -n db_ins@%%h -l DEBUG --concurrency=3 --queues=db_insert

celery -A simpletrader beat -l INFO --scheduler=django_celery_beat.schedulers:DatabaseScheduler


celery multi start wrk_api db_ins -A simpletrader -l WARNING \
    -c:db_ins 3 -c:wrk_api 100 \
    -P:wrk_api gevent \
    --pidfile=/tmp/%n.pid --logfile=/tmp/%n%I.log \
    -Q:wrk_api api_call -Q:db_ins db_insert