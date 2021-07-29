# simpletrader

celery -A simpletrader worker -l DEBUG -Q celery,high
celery -A simpletrader beat -l INFO --scheduler=django_celery_beat.schedulers:DatabaseScheduler