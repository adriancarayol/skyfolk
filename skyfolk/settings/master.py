from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# config e-mail
#                   https://docs.djangoproject.com/en/dev/topics/email/
#
# cuenta test de gmail para el envío de mails
# user: dfgsdfgsdf906@gmail.com
# pass: 56g4eD&%&FGfgdsf
#

EMAIL_HOST = 'localhost'
EMAIL_USE_TLS = False
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = '587'
#EMAIL_HOST_USER = 'dfgsdfgsdf906@gmail.com'
#EMAIL_HOST_PASSWORD = '56g4eD&%&FGfgdsf'

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/skyfolk/static/master/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/skyfolk/static/master/media'
