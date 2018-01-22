from __future__ import absolute_import, unicode_literals

VERSION = (0, 0, 1)  # PEP 386
__version__ = ".".join([str(x) for x in VERSION])

default_app_config = 'skyfolk.apps.SkyfolkConfig'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ['celery_app']