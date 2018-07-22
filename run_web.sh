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

# su -m skyfolk -c "command"
python manage.py makemigrations
python manage.py makemigrations badgify
python manage.py migrate badgify
python manage.py migrate
python manage.py badgify_sync badges
python manage.py badgify_sync badges --update
python manage.py install_labels
python manage.py rebuild_index --noinput
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('adrian', 'adriancarayol@gmail.com', 'un!x322@')" | python manage.py shell
# su -m skyfolk -c "python manage.py runserver 0.0.0.0:8000"
daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer

