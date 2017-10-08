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

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, 'skyfolk/media')

DEVELOP_APPS = (
    'django_extensions',
    'debug_toolbar'
)

INSTALLED_APPS = INSTALLED_APPS + DEVELOP_APPS

DEV_MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

MIDDLEWARE_CLASSES = DEV_MIDDLEWARE_CLASSES + MIDDLEWARE_CLASSES
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ALLOWED_HOSTS = ALLOWED_HOSTS + ['127.0.0.1','localhost', '0.0.0.0']
