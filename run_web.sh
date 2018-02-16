#!/bin/sh

sleep 10

# su -m skyfolk -c "command"
ls -lra /root/.imageio
su -m skyfolk -c "python manage.py compress"
su -m skyfolk -c "python manage.py collectstatic --noinput"
su -m skyfolk -c "python manage.py install_labels"
su -m skyfolk -c "python manage.py makemigrations"
su -m skyfolk -c "python manage.py makemigrations badgify"
su -m skyfolk -c "python manage.py migrate badgify"
su -m skyfolk -c "python manage.py migrate"
su -m skyfolk -c "python manage.py badgify_sync badges"
su -m skyfolk -c "python manage.py badgify_sync badges --update"
sleep 10
su -m skyfolk -c "python manage.py rebuild_index --noinput"
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('adrian', 'adriancarayol@gmail.com', 'un!x322@')" | python manage.py shell
# su -m skyfolk -c "python manage.py runserver 0.0.0.0:8000"
su -m skyfolk -c "daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer"

