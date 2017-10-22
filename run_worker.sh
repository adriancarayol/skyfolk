#!/bin/sh

sleep 10

ls -lra /root/.imageio

su -m skyfolk -c "python manage.py runworker -v2"
