import os
from django.core.exceptions import ImproperlyConfigured
from .base import *


# Cargamos SECRET_KEY
def get_env_variable(var_name):
    '''Intenta leer una variable de entorno'''
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

# Eliminar except
try:
    SECRET_KEY = get_env_variable('SECRET_KEY')
except:
    SECRET_KEY = '0)3c4u$y^+3&tx=rsgqsnr!=r5nl%j)w401o#86v97w%2v$99#'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_ENV_DB', 'skyfolk_pre_db'),
        'USER': os.environ.get('DB_ENV_POSTGRES_USER', 'skyfolk_pre'),
        'PASSWORD': os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'gDFgg$G=4h_%H'),
        'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', '45.55.57.214'),
        'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', '5433'),
    }
}
# NEO4J config
NEOMODEL_NEO4J_BOLT_URL = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:1518@45.55.57.214:7687')

# ACCOUNT SETTINGS FOR PRE
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
ALLOWED_HOSTS = ALLOWED_HOSTS + ['45.55.57.214']
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATIC_ROOT = '/var/www/skyfolk/static/pre/static'
MEDIA_ROOT = os.path.join(BASE_DIR, "skyfolk/media")
MEDIA_URL = '/media/'
# MEDIA_ROOT = '/var/www/skyfolk/static/pre/media'
# INVITATIONS ONLY EMAIL
INVITATIONS_INVITATION_ONLY = True

