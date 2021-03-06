#!/bin/bash

export PGPASSWORD="$DB_ENV_POSTGRES_PASSWORD"

until psql -h "$DB_PORT_5432_TCP_ADDR" -U "$DB_ENV_POSTGRES_USER" -d "$DB_ENV_DB" -c  '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - executing command"

rm celerybeat.pid
celery -A skyfolk beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
