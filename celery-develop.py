#!/usr/bin/env python
import os
import subprocess
import sys

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "skyfolk.settings.develop"
    os.environ["RABBIT_PORT_5672_TCP"] = "localhost:5672"
    os.environ['NEO4J_BOLT_URL'] = 'localhost'

    celery_worker = "celery -A skyfolk worker -l info"
    celery_beat = "celery -A skyfolk beat -l info"
    process = subprocess.Popen(celery_worker.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    process = subprocess.Popen(celery_beat.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
