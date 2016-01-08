from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'skyfolk_pre_db',
        'USER': 'skyfolk_pre',
        'PASSWORD': 'gDFgg$G=4h_%H',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/skyfolk/static/pre/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/skyfolk/static/pre/media'
