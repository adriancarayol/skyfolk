#!/bin/sh

sleep 10

su -m admin -c "celery worker -A skyfolk -Q default -n default@%h"
su -m admin -c "celery -A skyfolk beat"
