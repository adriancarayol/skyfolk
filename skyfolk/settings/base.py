"""
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os

from neomodel import config
from neomodel import db


BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DEBUG = False
ALLOWED_HOSTS = ['.skyfolk.net']
INTERNAL_IPS = ['127.0.0.1']

# Allowed html content.
ALLOWED_TAGS = "p div br code pre h1 h2 h3 h4 hr span s sub " \
               "sup b i img strong strike em underline super " \
               "table thead tr th td tbody".split()
ALLOWED_STYLES = 'color font-weight background-color width height'.split()
ALLOWED_ATTRIBUTES = {
    '*': ['style'],
    'a': ['href', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing'],
}

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
    'django.contrib.humanize',
)

# Third Party Applications
THIRD_PARTY_APPS = (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',  # REST framework

    # 'achievements',   # achivements       Portando a Python3
    'emoji',
    'avatar',  # Avatares para usuarios.
    'channels',  # django-channels
    'photologue',  # photologue original
    'sortedm2m',
    'taggit',  # para etiquetas
    'el_pagination',  # Para paginacion
    'notifications',  # notificaciones
    'dal',  # autocompletado
    'dal_select2',
    'django_celery_results',
    'easy_thumbnails',
    'dash',
    'dash.contrib.layouts.android',
    'dash.contrib.layouts.bootstrap2',
    'dash.contrib.layouts.windows8',
    'dash.contrib.plugins.dummy',
    'dash.contrib.plugins.image',
    'dash.contrib.plugins.memo',
    'dash.contrib.plugins.rss_feed',
    'dash.contrib.plugins.url',
    'dash.contrib.plugins.video',
    'dash.contrib.plugins.weather',
    'mptt',
    'tasks_server',
    'postman',
    'django_neomodel',
    'compressor',
    'storages',
    'corsheaders',
    'guardian',
    'embed_video',
    'tellme',
    'haystack',
)

FIRST_PARTY_APPS = (
    'landing',  # página de inicio
    'user_profile',  # perfil de usuario
    'publications',  # publicaciones en el perfil
    'publications_gallery', # publicaciones en galeria
    'publications_groups', # publicaciones en grupos
    'about',  # sobre los autores
    'latest_news',
    'user_groups',  # Para grupos de usuarios
    'support',  # modulo para ofrecer soporte al usuario
)

INSTALLED_APPS = DEFAULT_APPS + FIRST_PARTY_APPS + THIRD_PARTY_APPS

# DJANGO ALL AUTH CONFIG
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_NAME = None

# auth and allauth settings
LOGIN_REDIRECT_URL = '/'
# SOCIALACCOUNT_QUERY_EMAIL = True
# SOCIALACCOUNT_PROVIDERS = {
#    'facebook': {
#        'SCOPE': ['email', 'publish_stream'],
#        'METHOD': 'js_sdk'  # instead of 'oauth2'
#    }
# }

ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_ADAPTER = 'user_profile.adapter.MyAccountAdapter'
ACCOUNT_FORMS = {'login': 'user_profile.forms.CustomLoginForm'}
ACCOUNT_SIGNUP_FORM_CLASS = 'user_profile.forms.SignupForm'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'
ACCOUNT_AUTHENTICATION_METHOD = ("username_email")
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/accounts/login'
EXTERNAL_LOGIN_URL = None
EXTERNAL_SIGNUP_URL = None
EXTERNAL_LOGOUT_URL = None
# / DJANGO ALL AUTH CONFIG

# CONFIG E-MAIL
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'skyfolk <no-reply@skyfolk.net>'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# SESSION EXPIRATION
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_UPDATE_SECONDS = 10 * 60
# REST FRAMEWORK
#                   http://www.django-rest-framework.org/
REST_FRAMEWORK = {
    # hace la api solo accesible para admins
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    # paginado de la api
    'PAGINATE_BY': 10
}
# /REST FRAMEWORK

# django-taggit
TAGGIT_CASE_INSENSITIVE = True

# NOTIFICATION
NOTIFICATIONS_USE_JSONFIELD = True

# neo4j database

config.DATABASE_URL = 'bolt://neo4j:1518@localhost:7687'  # default
NEOMODEL_NEO4J_BOLT_URL = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:1518@localhost:7687')
NEOMODEL_ENCRYPTED_CONNECTION = True
NEOMODEL_SIGNALS = True

db.set_connection('bolt://neo4j:1518@localhost:7687')

# cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

USER_ONLINE_TIMEOUT = 300
USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7

# CACHE BACK_IMAGE
BACK_IMAGE_CACHE_TIMEOUT = 300
BACK_IMAGE_DEFAULT_SIZE = 1024 * 1024 * 5
VIDEO_EXTENTIONS = ["avi", "mp4"]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'user_profile.middleware.ActiveUserMiddleware',
    'skyfolk.middleware.AutoLogout',
    'corsheaders.middleware.CorsMiddleware',
)

CORS_ORIGIN_WHITELIST = (
    'pre.skyfolk.net',
    'skyfolk.net',
    'localhost:8000',
    '127.0.0.1:8000'
)

# Auto logout delay in minutes - 1 mes
AUTO_LOGOUT_DELAY = 60

# Configuracion para django-el-pagination

EL_PAGINATION_LOADING = """<img src="/static/img/ripple.gif" alt="loading" />"""
EL_PAGINATION_PER_PAGE = 20

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
                # Required by allauth template tags
                # allauth specific context processors
                # "allauth.account.context_processors.account",
                # "allauth.socialaccount.context_processors.socialaccount",
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'user_profile.custom_context.user_processor',
            ],
        },
    },
]

# rabbitmq
rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
rabbitmq_url = 'amqp://guest:guest@%s:5672/%%2F?heartbeat=15' % rabbitmq_host

# celery
CELERY_CONFIG = 'skyfolk.celeryconf'
CELERY_RESULT_BACKEND = 'django-db'
# https://channels.readthedocs.io/en/latest/deploying.html#setting-up-a-channel-backend

CHANNEL_LAYERS = {
    "default": {
        'BACKEND': 'asgi_rabbitmq.RabbitmqChannelLayer',
        "CONFIG": {
            "url": rabbitmq_url
        },
        "ROUTING": "skyfolk.routing.channel_routing",
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# FILE_CHARSET="utf-8"

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
# STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "skyfolk/static"),
)

COMPRESS_ENABLED = True
# COMPRESS_OFFLINE = True
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# Media (uploads, ...)
# MEDIA_ROOT = os.path.join(os.path.join(BASE_DIR, 'skyfolk'), 'media')
# MEDIA_URL = '/media/'

# NOTIFICACIONES
''' Marca las notificaciones como borradas
    en vez de eliminarlas de la base de datos.'''
NOTIFICATIONS_SOFT_DELETE = True
''' Permite enviar datos arbitrarios en las notificaciones '''
NOTIFICATIONS_USE_JSONFIELD=True

ADMINS = (
    ('Adrian Carayol', 'adriancarayol@gmail.com'),
    ('Gabriel Fernandez', 'gabofer82@gmail.com'),
    ('lostcitizen', 'lostcitizen@gmail.com'),
)
# Para emails al recibir nuevo feedback

TELLME_FEEDBACK_EMAIL = 'adriancarayol@gmail.com'

MANAGERS = ADMINS
POSTMAN_AUTO_MODERATE_AS = True

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         'URL': 'http://127.0.0.1:8080/solr/',
#     },
# }


HAYSTACK_CONNECTIONS = {
    'default': {
      'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
      'PATH': os.path.join(BASE_DIR, 'whoosh_index')
    },
  }

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 100
