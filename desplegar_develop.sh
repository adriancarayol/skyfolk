#!/bin/bash

echo "Aplicando migraciones" && \
python manage.py makemigrations && python manage.py migrate && \
python manage.py install_labels && \
python manage.py migrate badgify && \
python manage.py migrate && \
python manage.py badgify_sync badges && \
python manage.py badgify_sync badges --update && \

echo "Actualizando indices de elasticsearch" && \
python manage.py rebuild_index --noinput && \
echo "Lanzando proyecto" && \
python manage.py runserver 


