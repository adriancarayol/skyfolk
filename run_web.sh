#!/bin/sh

sleep 10

# su -m skyfolk -c "command"

su -m skyfolk -c "python manage.py install_labels"
su -m skyfolk -c "python manage.py makemigrations"
su -m skyfolk -c "python manage.py makemigrations badgify"
su -m skyfolk -c "python manage.py migrate badgify"
su -m skyfolk -c "python manage.py migrate"
su -m skyfolk -c "python manage.py badgify_sync badges"
su -m skyfolk -c "python manage.py badgify_sync badges --update"
sleep 10
su -m skyfolk -c "python manage.py rebuild_index --noinput"
su -m skyfolk -c "python manage.py runserver 0.0.0.0:8000"
# python manage.py runworker --only-channels=http.* --only-channels=websocket.* -v2
# daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer

