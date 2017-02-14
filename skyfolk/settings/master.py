from .base import *


# Cargamos SECRET_KEY
def get_env_variable(var_name):
    '''Intenta leer una variable de entorno'''
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_env_variable('SECRET_KEY')

DEBUG = False
ALLOWED_HOSTS = ['.skyfolk.net', '127.0.0.1']

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
