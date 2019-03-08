import os
from .base import *

SECRET_KEY = 'develop'
DEBUG = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_USE_TLS = False


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}

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

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, 'skyfolk/media')

# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ALLOWED_HOSTS = ['*']


# ELASTICSEARCH CONFIGURATION
ELASTIC_URL = os.environ.get('ELASTICSEARCH_URL', 'localhost')

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
#         'URL': 'http://{elastic_host}:9200/'.format(elastic_host=ELASTIC_URL),
#         'INDEX_NAME': 'haystack',
#     },
# }
