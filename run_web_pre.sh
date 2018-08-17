#!/bin/sh

export PGPASSWORD="$DB_ENV_POSTGRES_PASSWORD"

until psql -h "$DB_PORT_5432_TCP_ADDR" -U "$DB_ENV_POSTGRES_USER" -d "$DB_ENV_DB" -c  '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

while [[ "$(curl --write-out ''%{http_code}'' --silent --output /dev/null --user ''$NEO4J_USER':'$NEO4J_PASSWORD'' 'http://'$NEO4J_HOST':7474/user/neo4j')" != "200" ]]; do
	>&2 echo "neo4j is unavailable - sleeping"
	sleep 5; 
done

>&2 echo "neo4j is up - executing command"

python manage.py --entorno pre collectstatic --noinput
python manage.py --entorno pre makemigrations
python manage.py --entorno pre makemigrations badgify
python manage.py --entorno pre migrate badgify
python manage.py --entorno pre migrate
python manage.py --entorno pre badgify_sync badges
python manage.py --entorno pre badgify_sync badges --update
python manage.py --entorno pre install_labels
python manage.py --entorno pre rebuild_index --noinput
python manage.py create_initial_services
daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer

