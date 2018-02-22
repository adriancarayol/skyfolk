#!/bin/bash

sleep 10

ls -lra /root/.imageio

celery -A skyfolk worker -l info
