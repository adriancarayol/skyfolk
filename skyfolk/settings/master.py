from .base import *


DEBUG = False
ALLOWED_HOSTS = ['.skyfolk.net','127.0.0.1']

EMAIL_HOST = 'localhost'
EMAIL_USE_TLS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'skyfolk_db',
        'USER': 'skyfolk',
        'PASSWORD': 'v4g$h45HgY$%Y',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/skyfolk/static/master/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/skyfolk/static/master/media'
