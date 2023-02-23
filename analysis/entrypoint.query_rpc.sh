#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z analysisdb 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

celery -A simpletrader worker --pool gevent --concurrency 128 --loglevel warning -Q analysis_query
