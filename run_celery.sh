#!/bin/bash

sleep 10

celery -A skyfolk worker -l info
