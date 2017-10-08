#!/bin/bash

sleep 10

su -m skyfolk -c "celery -A skyfolk worker --loglevel=info"
su -m skyfolk -c "celery -A skyfolk beat --loglevel=info"
