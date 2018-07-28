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

ls -lra /root/.imageio

python manage.py runworker -v2
