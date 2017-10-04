#!/bin/bash

sleep 10

su -m skyfolk -c "python manage.py install_labels"
su -m skyfolk -c "python manage.py makemigrations"
su -m skyfolk -c "python manage.py makemigrations badgify"
su -m skyfolk -c "python manage.py migrate"
su -m skyfolk -c "python manage.py badgify_sync badges"
su -m skyfolk -c "python manage.py badgify_sync badges --update"
su -m skyfolk -c "python manage.py rebuild_index"
su -m skyfolk -c "daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer"
su -m skyfolk -c "python manage.py runworker -v2"

