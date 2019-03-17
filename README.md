# SKYFOLK - PROJECT

## Getting Started

### Pre-requisitos
Necesitamos tener el siguiente software instalado en el ordenador:
A continuación se muestra <software:version_a_instalar>
```
elasticsearch: 2.3.1 (https://www.elastic.co/downloads/past-releases/elasticsearch-2-4-6)
redis:latest
rabbitmq:latest
ffmpeg:latest
postgresql:latest
neo4j:latest
tidy:latest
pandoc:latest
npm -g install yuglify
```
Tras esto, podemos instalar los requerimentos de la siguiente forma:
```
apt install python python-dev python-pip python-virtualenv build-essential
pip install -r requeriments/develop.txt
```
Para cambiar el password de neo4j, introducimos el siguiente comando:
```
curl -H "Content-Type: application/json" -X POST -d '{"password":"NUEVA_PASSWORD"}' -u neo4j:neo4j http://localhost:7474/user/neo4j/password
```
Comprobamos también que estén TODOS los servicios activos con el comando:
```
systemctl status service
```
Según el entorno de desarrollo, hay unas variables de entorno definidas, por ejemplo, en settings/base.py
REDIS coge el host a partir de una variable de entorno, al igual que RabbitMQ en skyfolk/celeryconf.py, o en settings/pre.py
Para ver las variables de entorno existentes, podemos entrar a manage.py y según la rama en la que estemos se establecerán unas por defecto.
```
```
### Lanzar la aplicación
Comenzamos con las migraciones y ponemos en marcha el proyecto.
```
find . -name "*.pyc" -exec rm -f {} \;
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py makemigrations badgify
python manage.py migrate badgify
python manage.py migrate
python manage.py badgify_sync badges
python manage.py badgify_sync badges --update
python manage.py sync_ranks
daphne -b 0.0.0.0 -p 8000 skyfolk.asgi:application
```
### Lanzar celery
Para lanzar celery debemos lanzar los siguientes comandos:
```
celery -A skyfolk worker -l info
celery -A skyfolk beat -l info
```
### Lanzar con Docker
Antes de nada, debemos desactivar los servicios de rabbitmq-server, redis-server y elasticsearch con el comando:
```
systemctl stop rabbitmq-server
systemctl stop redis-server
systemctl stop elasticsearch
```
Si estamos en develop, los comandos son los siguientes:
```
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d
```
Si estamos en pre, los comandos son los siguientes:
```
docker-compose -f docker-compose-pre.yml build
docker-compose -f docker-compose-pre.yml up -d
```
nginx también está dockerizado, el archivo de configuración que coge está en skyfolk/conf/skyfolk.conf, que hay que configurar convenientemente para que funcione, por defecto el host es localhost, para pre/master habrá que cambiar a skyfolk.net o pre.skyfolk.net

Para que funcione el servidor de correo, debemos modificar el fichero /etc/postfix/main.cf:
```
mynetworks = 172.0.0.0/8, 172.22.0.0/16
smtpd_recipient_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination
smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination
```
Reiniciamos el servidor postfix con:
```
systemctl restart postfix
```

Lanzar app de go
```
export GOPATH=/var/www/skyfolk.net/run/app
cd ${GOPATH}/src/skyfolk_services && dep ensure
exec /usr/bin/go run ${GOPATH}/src/skyfolk_services/cmd/main/main.go

```

### Problemas con ASCII
Instalar es_ES-UTF-8 y setearlo por defecto.