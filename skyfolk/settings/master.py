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

STATICFILES_STORAGE = 'custom_storages.custom_storages.CachedS3BotoStorage'

AWS_ACCESS_KEY_ID = 'AKIAJYNH343VWWRAP2EA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'skyfolk.net'
AWS_S3_SIGNATURE_VERSION = 's3v4'

STATIC_ROOT = os.path.join(BASE_DIR, "static")
COMPRESS_ROOT = STATIC_ROOT
STATICFILES_LOCATION = 'static'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.custom_storages.MediaStorage'

COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = 'custom_storages.custom_storages.CachedS3BotoStorage'

# ACCOUNT SETTINGS FOR PRE
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

#STATIC_URL = '/static/'
#STATIC_ROOT = '/var/www/skyfolk/static/master/static'
#MEDIA_URL = '/media/'
#MEDIA_ROOT = '/var/www/skyfolk/static/master/media'
