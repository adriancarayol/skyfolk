# SKYFOLK - PROJECT

## Getting Started

### Pre-requisitos
Necesitamos tener el siguiente software instalado en el ordenador:
A continuación se muestra <software:version_a_instalar>
```
elasticsearch: 2.3.1
redis:latest
rabbitmq:latest
ffmpeg:latest
postgresql:latest
neo4j:latest
```
Tras esto, podemos instalar los requerimentos de la siguiente forma:
```
pip install -r requeriments/develop.txt
```
Según el entorno de desarrollo, hay unas variables de entorno definidas, por ejemplo, en settings/base.py
REDIS coge el host a partir de una variable de entorno, al igual que RabbitMQ en skyfolk/celeryconf.py, o en settings/pre.py
Para ver las variables de entorno existentes, podemos entrar a manage.py y según la rama en la que estemos se establecerán unas por defecto.
```
```
### Lanzar la aplicación
Comenzamos con las migraciones y ponemos en marcha el proyecto.
```
python manage.py collectstatic --noinput
python manage.py install_labels
python manage.py makemigrations
python manage.py makemigrations badgify
python manage.py migrate badgify
python manage.py migrate
python manage.py badgify_sync badges
python manage.py badgify_sync badges --update
python manage.py rebuild_index --noinput
python manage.py runserver 0.0.0.0:8000
daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:channel_layer
```
### Lanzar celery
Para lanzar celery debemos lanzar los siguientes comandos:
```
celery -A skyfolk worker -l info
celery -A skyfolk beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
