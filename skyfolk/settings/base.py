"""
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DEBUG = False
ALLOWED_HOSTS = ['.skyfolk.net','127.0.0.1']

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
    'allauth',
    # 'photologue',            # Galeria photologue.
    # 'sortedm2m',             # Galeria photologue.
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',          # REST framework
    'django_messages',         # mensajes entre usuarios
    #'achievements',            # achivements       Portando a Python3
    'emoji',
    'avatar',                  # Avatares para usuarios.
    'notifications',           # siempre último
)

FIRST_PARTY_APPS = (
    'landing',                 # página de inicio
    'user_profile',            # perfil de usuario
    'publications',            # publicaciones en el perfil
    'text_processor',          # Formatea un texto para incorporar emoticonos, hashtags...
    'timeline',
    'about',                   # sobre los autores
    'latest_news',
)

INSTALLED_APPS = DEFAULT_APPS + FIRST_PARTY_APPS + THIRD_PARTY_APPS

# DJANGO ALL AUTH CONFIG
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
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'
ACCOUNT_AUTHENTICATION_METHOD = ("username_email")
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/accounts/login'
# / DJANGO ALL AUTH CONFIG

# CONFIG E-MAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'skyfolk <no-reply@skyfolk.net>'
# SESSION EXPIRATION
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
# REST FRAMEWORK
#                   http://www.django-rest-framework.org/
REST_FRAMEWORK = {
    # hace la api solo accesible para admins
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    # paginado de la api
    'PAGINATE_BY': 10
}
# /REST FRAMEWORK

#NOTIFICATION
NOTIFICATIONS_USE_JSONFIELD=True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'skyfolk.middleware.AutoLogout',
)

# Auto logout delay in minutes - 1 mes
AUTO_LOGOUT_DELAY = 60

ROOT_URLCONF = 'skyfolk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                    os.path.join(BASE_DIR, 'skyfolk/templates')
                ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Required by allauth template tags
                "django.core.context_processors.request",
                # allauth specific context processors
                #"allauth.account.context_processors.account",
                #"allauth.socialaccount.context_processors.socialaccount",
                "django.core.context_processors.static",
                "django.core.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = 'skyfolk.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True
#FILE_CHARSET="utf-8"

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "skyfolk/static"),
)

# Media (uploads, ...)
MEDIA_ROOT = os.path.join(os.path.join(BASE_DIR, 'skyfolk'), 'media')
MEDIA_URL = '/media/'

# NOTIFICACIONES
''' Marca las notificaciones como borradas
    en vez de eliminarlas de la base de datos.'''
NOTIFICATIONS_SOFT_DELETE = True
''' Permite enviar datos arbitrarios en las notificaciones '''
NOTIFICATIONS_USE_JSONFIELD = True

ADMINS = (
    ('Adrian Carayol', 'adriancarayol@gmail.com'),
    ('Gabriel Fernandez', 'gabofer82@gmail.com'),
    ('lostcitizen', 'lostcitizen@gmail.com'),
)
MANAGERS = ADMINS
