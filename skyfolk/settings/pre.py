import os
from django.core.exceptions import ImproperlyConfigured
from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Cargamos SECRET_KEY
def get_env_variable(var_name):
    '''Intenta leer una variable de entorno'''
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

ALLOWED_HOSTS += ['127.0.0.1']
SECRET_KEY = get_env_variable('SECRET_KEY')

DEBUG = True
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_ENV_DB', 'skyfolk_pre_db'),
        'USER': os.environ.get('DB_ENV_POSTGRES_USER', 'skyfolk_pre'),
        'PASSWORD': os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'gDFgg$G=4h_%H'),
        'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', 'localhost'),
        'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', '5432'),
    }
}
# NEO4J config
NEOMODEL_NEO4J_BOLT_URL = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:1518@localhost:7687')

# ACCOUNT SETTINGS FOR PRE
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/skyfolk.net/run/static/static/"
# STATIC_ROOT = '/var/www/skyfolk/static/pre/static'
MEDIA_ROOT = "/var/www/skyfolk.net/run/static/media/"
MEDIA_URL = '/media/'
# MEDIA_ROOT = '/var/www/skyfolk/static/pre/media'
# INVITATIONS ONLY EMAIL
INVITATIONS_INVITATION_ONLY = True

# ELASTICSEARCH CONFIGURATION
ELASTIC_URL = os.environ.get('ELASTICSEARCH_URL', 'localhost')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://{elastic_host}:9200/'.format(elastic_host=ELASTIC_URL),
        'INDEX_NAME': 'haystack',
    },
}
