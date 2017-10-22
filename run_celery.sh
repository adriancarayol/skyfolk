#!/bin/bash

sleep 10

ls -lra /root/.imageio

su -m skyfolk -c "celery -A skyfolk worker -l info"
