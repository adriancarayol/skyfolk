#!/bin/sh

sleep 10

ls -lra /root/.imageio

python manage.py runworker -v2
