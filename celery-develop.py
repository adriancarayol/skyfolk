#!/usr/bin/env python
import os
import subprocess
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "skyfolk.settings.develop"

celery_worker = "celery -A skyfolk worker -l info"
celery_beat = "celery -A skyfolk beat"
process = subprocess.Popen(celery_worker.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
process = subprocess.Popen(celery_beat.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
