#!/bin/bash

export PGPASSWORD="$DB_ENV_POSTGRES_PASSWORD"

until psql -h "$DB_PORT_5432_TCP_ADDR" -U "$DB_ENV_POSTGRES_USER" -d "$DB_ENV_DB" -c  '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

python manage.py makemigrations
python manage.py makemigrations badgify
python manage.py migrate badgify
python manage.py migrate
python manage.py badgify_sync badges
python manage.py badgify_sync badges --update
python manage.py install_labels
python manage.py rebuild_index --noinput
python manage.py create_initial_services
python manage.py runserver 0.0.0.0:8000