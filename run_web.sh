#!/bin/bash

sleep 10

su -m admin -c "python manage.py install_labels"
su -m admin -c "python manage.py makemigrations"
su -m admin -c "python manage.py makemigrations badgify"
su -m admin -c "python manage.py migrate"
su -m admin -c "python manage.py badgify_sync badges"
su -m admin -c "python manage.py badgify_sync badges --update"
su -m admin -c "python manage.py rebuild_index"
su -m admin -c "daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer"
su -m admin -c "python manage.py runworker -v2"

