#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z analysisdb_pgbouncer 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py migrate
python manage.py loaddata assets exchanges pairs markets orderStates
python manage.py run_collectors
