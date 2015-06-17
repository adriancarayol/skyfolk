#encoding:utf-8
"""
Django settings for skyfolk project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Identificando la ruta de la raiz del proyecto
import os
RAIZ_PROYECTO = os.path.dirname(os.path.realpath(__file__))

gettext = lambda s: s
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z_v9kx(!^1bqmedpn65t#*4t=6(0*17co+$%f!0vtug19xic()'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition
DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admindocs',
)

# Third Party Applications
THIRD_PARTY_APPS = (
    # 'south',                 # Gestiona las migraciones de bdd
    'allauth',
    # 'photologue',              # Galeria photologue.
    # 'sortedm2m',	       # Galeria photologue.
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',          # REST framework
    'django_messages',         # mensajes entre usuarios
    'emoji',
)

# Local Applications
LOCAL_APPS = (
    'landing',
    'user_profile',
    'publications',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

####################################################
# DJANGO ALL AUTH CONFIG
####################################################


TEMPLATE_CONTEXT_PROCESSORS = (
    # Required by allauth template tags
    "django.core.context_processors.request",
    # allauth specific context processors
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

# auth and allauth settings
LOGIN_REDIRECT_URL = '/'
#SOCIALACCOUNT_QUERY_EMAIL = True
#SOCIALACCOUNT_PROVIDERS = {
#    'facebook': {
#        'SCOPE': ['email', 'publish_stream'],
#        'METHOD': 'js_sdk'  # instead of 'oauth2'
#    }
#}

ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_ADAPTER = 'user_profile.adapter.MyAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'user_profile.forms.SignupForm'
ACCOUNT_LOGOUT_REDIRECT_URL ='/accounts/login'
####################################################
# / DJANGO ALL AUTH CONFIG
####################################################

##########################################################################
# Configuración servidor SMTP envio de correos
# 20140316 - Instalación
##########################################################################
#                   https://docs.djangoproject.com/en/dev/topics/email/
#
# cuenta test de gmail para el envío de mails
# user: dfgsdfgsdf906@gmail.com
# pass: 56g4eD&%&FGfgdsf
#
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'dfgsdfgsdf906@gmail.com'
#EMAIL_HOST_PASSWORD = '56g4eD&%&FGfgdsf'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

##########################################################################
# REST FRAMEWORK
# 20140402 - Instalación
##########################################################################
#                   http://www.django-rest-framework.org/
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 10
}

ROOT_URLCONF = 'skyfolk.urls'

WSGI_APPLICATION = 'skyfolk.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Or path to database file if using sqlite3.
        #'NAME': 'skyfolk_db',
        #'USER': 'postgres',
        #'PASSWORD': 'Palindromos_720',
        # Or path to database file if using sqlite3.
        'NAME': 'skyfolkdb',
        'USER': 'skyfolk',
        'PASSWORD': 'EB6E736224B550A605BD62A72CA47285'
                    'D608107FE990362469B1EFF287277648',
        # Empty for localhost through domain sockets or
        # '127.0.0.1' for localhost through TCP.
        'HOST': 'localhost',
        # Set to empty string for default.
        'PORT': '',
    }
}

#DATABASES = {
#    'default': {
#        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        # Or path to database file if using sqlite3.
#        #'NAME': 'skyfolk_db',
#        #'USER': 'postgres',
#        #'PASSWORD': 'Palindromos_720',
#        # Or path to database file if using sqlite3.
#        'NAME': 'd27f8if9fbfjgl',
#        'USER': 'iqzsahhpuvthkp',
#        'PASSWORD': 'H9UoSdDil39_Z3TRjj_gn7JMja',
#        # Empty for localhost through domain sockets or
#        # '127.0.0.1' for localhost through TCP.
#        'HOST': 'ec2-54-247-107-140.eu-west-1.compute.amazonaws.com',
#        # Set to empty string for default.
#        'PORT': '5432',
#    }
#}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es-ES'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

# Media (uploads, ...)
MEDIA_ROOT = os.path.join(RAIZ_PROYECTO,'media')
MEDIA_URL = '/media/'

# Identificador
SITE_ID = 1

ADMINS = (
    ('Adrian Carayol', 'adriancarayol@gmail.com'),
    ('Carlos Canicio', 'canicio7@gmail.com'),
    ('Lostcitizen', 'lostcitizen@gmail.com'),
)

TEMPLATE_DIRS = (
    os.path.join(RAIZ_PROYECTO, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(RAIZ_PROYECTO, 'static'),
)

##...................................................................

# heroku

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] = dj_database_url.config()
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Allow all host headers
ALLOWED_HOSTS = ['*']
# Static asset configuration
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

#..................................................................
