import os
from django.core.exceptions import ImproperlyConfigured
from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS += ['127.0.0.1']
SECRET_KEY = os.environ.get('SECRET_KEY','NO-SECRET')
SESSION_COOKIE_DOMAIN = '.skyfolk.net'
# S3 + CDN
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_CUSTOM_DOMAIN = 'd32rim3h420riw.cloudfront.net'
AWS_ACCESS_KEY_ID = 'AKIAJYNH343VWWRAP2EA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'skyfolk'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_PRELOAD_METADATA = True
# S3_USE_SIGV4 = True
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN


MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_ROOT = "/var/www/skyfolk.net/run/static/media/"
THUMBNAIL_DEFAULT_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# MEDIA_ROOT = MEDIA_URL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_ENV_DB', 'skyfolk_db'),
        'USER': os.environ.get('DB_ENV_POSTGRES_USER', 'skyfolk'),
        'PASSWORD': os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'G·$_-)(G45g45g'),
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
# STATIC_URL = '/static/'
# STATIC_ROOT = "/var/www/skyfolk.net/run/static/static/"
# STATIC_ROOT = '/var/www/skyfolk/static/pre/static'
# MEDIA_ROOT = "/var/www/skyfolk.net/run/static/media/"
# MEDIA_URL = '/media/'
# MEDIA_ROOT = '/var/www/skyfolk/static/pre/media'
# INVITATIONS ONLY EMAIL
INVITATIONS_INVITATION_ONLY = True

# ELASTICSEARCH CONFIGURATION
ELASTIC_URL = os.environ.get('ELASTICSEARCH_URL', 'localhost')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
        'URL': 'http://{elastic_host}:9200/'.format(elastic_host=ELASTIC_URL),
        'INDEX_NAME': 'haystack',
    },
}
