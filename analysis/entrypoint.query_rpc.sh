#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z analysisdb_pgbouncer 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

celery -A simpletrader worker --concurrency 12 --loglevel warning -Q analysis_query
