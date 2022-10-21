#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z traderdb 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py migrate --database=traderdb
celery -A simpletrader worker -l INFO --pool=gevent --concurrency=64 --queues=trader
