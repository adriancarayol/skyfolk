#!/bin/sh

sleep 10

su -m admin -c "python manage.py install_labels"
su -m admin -c "python manage.py makemigrations"
su -m admin -c "python manage.py makemigrations badgify"
su -m admin -c "python manage.py migrate"
su -m admin -c "python manage.py badgify_sync badges"
su -m admin -c "python manage.py badgify_sync badges --update"

su -m admin -c "python manage.py runserver 127.0.0.1:8000"

