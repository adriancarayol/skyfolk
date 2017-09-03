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
# ACCOUNT SETTINGS FOR PRE
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/skyfolk/static/pre/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/skyfolk/static/pre/media'
