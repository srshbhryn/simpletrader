#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z timescale_db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py migrate --database=timescale
python manage.py nobitex_reinit
python manage.py nobitex__collect_trades

