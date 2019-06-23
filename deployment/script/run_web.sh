#!/bin/sh

export PGPASSWORD="$DB_ENV_POSTGRES_PASSWORD"

until psql -h "$DB_PORT_5432_TCP_ADDR" -U "$DB_ENV_POSTGRES_USER" -d "$DB_ENV_DB" -c  '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - executing command"

# Provision application
python manage.py --entorno master collectstatic --noinput && \
python manage.py --entorno master makemigrations && \
python manage.py --entorno master makemigrations badgify && \
python manage.py --entorno master migrate badgify && \
python manage.py --entorno master migrate && \
python manage.py --entorno master badgify_sync badges && \
python manage.py --entorno master badgify_sync badges --update && \
python manage.py --entorno master sync_ranks

daphne -b 0.0.0.0 -p 8090 skyfolk.asgi:channel_layer

