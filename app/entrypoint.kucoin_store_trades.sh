#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z timescale_db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py migrate --database=timescale
python manage.py kucoin__reinit_markets
python manage.py kucoin__store_trades
