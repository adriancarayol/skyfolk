#!/bin/sh

sleep 10

# su -m skyfolk -c "command"

python manage.py install_labels
python manage.py makemigrations
python manage.py makemigrations badgify
python manage.py migrate badgify
python manage.py migrate
python manage.py badgify_sync badges
python manage.py badgify_sync badges --update
sleep 10
python manage.py rebuild_index --noinput
python manage.py runserver 0.0.0.0:8000
# python manage.py runworker --only-channels=http.* --only-channels=websocket.* -v2
# daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer

