#!/bin/bash

export PGPASSWORD="$DB_ENV_POSTGRES_PASSWORD"

until psql -h "$DB_PORT_5432_TCP_ADDR" -U "$DB_ENV_POSTGRES_USER" -d "$DB_ENV_DB" -c  '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - executing command"

celery -A skyfolk worker -l info
