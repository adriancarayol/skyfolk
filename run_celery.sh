#!/bin/bash

sleep 10

su -m skyfolk -c "celery worker -A skyfolk -Q default -n default@%h"
su -m skyfolk -c "celery -A skyfolk beat"
