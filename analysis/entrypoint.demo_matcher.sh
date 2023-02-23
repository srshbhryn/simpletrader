#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z analysisdb 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py demo_matcher__run
