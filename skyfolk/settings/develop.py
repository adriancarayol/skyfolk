import os
from django.conf.global_settings import SECRET_KEY
from .base import *

SECRET_KEY = 'develop'

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# NEO4j config
NEOMODEL_NEO4J_BOLT_URL = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:1518@localhost:7687')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, 'skyfolk/media')

DEVELOP_APPS = (
    'django_extensions',
)

INSTALLED_APPS = INSTALLED_APPS + DEVELOP_APPS

MIDDLEWARE_CLASSES =  MIDDLEWARE_CLASSES
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ALLOWED_HOSTS = ALLOWED_HOSTS + ['127.0.0.1','localhost', '0.0.0.0']

# ELASTICSEARCH CONFIGURATION
ELASTIC_URL = os.environ.get('ELASTICSEARCH_URL', 'localhost')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
        'URL': 'http://{elastic_host}:9200/'.format(elastic_host=ELASTIC_URL),
        'INDEX_NAME': 'haystack',
    },
}
