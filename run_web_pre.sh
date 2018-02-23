#!/bin/sh

sleep 10

# su -m skyfolk -c "command"
python manage.py --entorno pre compress
python manage.py --entorno pre collectstatic --noinput
python manage.py --entorno pre install_labels
python manage.py --entorno pre makemigrations
python manage.py --entorno pre makemigrations badgify
python manage.py --entorno pre migrate badgify
python manage.py --entorno pre migrate
python manage.py --entorno pre badgify_sync badges
python manage.py --entorno pre badgify_sync badges --update
sleep 10
python manage.py --entorno pre rebuild_index --noinput
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('adrian', 'adriancarayol@gmail.com', 'un!x322@')" | python manage.py shell
# su -m skyfolk -c "python manage.py runserver 0.0.0.0:8000"
daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer

