"""
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DEBUG = False
ALLOWED_HOSTS = ['.skyfolk.net', '158.69.59.134']
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
    'allauth.socialaccount.providers.google',
    'rest_framework',  # REST framework
    'emoji',
    'avatar',  # Avatares para usuarios.
    'channels',  # django-channels
    'photologue',  # photologue original
    'photologue_groups',  # photologue groups
    'sortedm2m',
    'taggit',  # para etiquetas
    'el_pagination',  # Para paginacion
    'notifications',  # notificaciones
    'django_celery_results',
    'formtools',
    'collectfast',
    'django_js_reverse',
    'external_services',
    'external_services.twitter',
    'dash',
    'dash.contrib.layouts.skyspace',
    'dash.contrib.layouts.profile',
    'dash.contrib.plugins.dummy',
    'dash.contrib.plugins.service',
    'dash.contrib.plugins.image',
    'dash.contrib.plugins.memo',
    'dash.contrib.plugins.rss_feed',
    'dash.contrib.plugins.url',
    'dash.contrib.plugins.statistics',
    'dash.contrib.plugins.follows',
    'dash.contrib.plugins.video',
    'dash.contrib.plugins.weather',
    'dash.contrib.plugins.poll',
    'dash.contrib.plugins.twitch',
    'mptt',
    'tasks_server',
    'postman',
    'easy_thumbnails',
    'storages',
    'corsheaders',
    'guardian',
    'embed_video',
    'haystack',
    'django_elasticsearch_dsl',
    'badgify',
    'invitations',
    'webpack_loader',
    'user_guide',
    'graphene_django',
    'celery_haystack',
    'django_extensions',
    'cookielaw',
    'ckeditor',
    'debug_toolbar',
)

FIRST_PARTY_APPS = (
    'user_profile',  # perfil de usuario
    'publications',  # publicaciones en el perfil
    'publications_gallery',  # publicaciones en galeria
    'publications_groups',  # publicaciones en grupos
    'publications_groups.themes',  # publicaciones para temas
    'publications_gallery_groups',
    'user_groups.configuration',
    'about',  # sobre los autores
    'latest_news',
    'user_groups',  # Para grupos de usuarios
    'support',  # modulo para ofrecer soporte al usuario
    'awards',  # logros
    'api',
    'api.user_profile_api',
    'feedback',
    'information'
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
SOCIALACCOUNT_ADAPTER = 'user_profile.adapter.MySocialAccountAdapter'
ACCOUNT_FORMS = {'login': 'user_profile.forms.CustomLoginForm'}
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_MAX_LENGTH = 15
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/accounts/login'
# Avatar settings
AVATAR_DEFAULT_SIZE = 140
AVATAR_PROVIDERS = (
    'avatar.providers.PrimaryAvatarProvider',
    'avatar.providers.GravatarAvatarProvider',
    'avatar.providers.DefaultAvatarProvider',
)
AVATAR_GRAVATAR_FORCEDEFAULT = False
AVATAR_GRAVATAR_FIELD = 'email'
AVATAR_GRAVATAR_BASE_URL = 'https://www.gravatar.com/avatar/'
AVATAR_CACHE_TIMEOUT = 60 * 60

EXTERNAL_LOGIN_URL = None
EXTERNAL_SIGNUP_URL = None
EXTERNAL_LOGOUT_URL = None

# AVATAR CONFIGURATION
AVATAR_GRAVATAR_DEFAULT = 'https://d32rim3h420riw.cloudfront.net/img/nuevo.png'

# / DJANGO ALL AUTH CONFIG

# CONFIG E-MAIL
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'no-reply@skyfolk.net'
EMAIL_HOST_PASSWORD = 'uLL:4jrpd(g5jgH!'
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@skyfolk.net'
# SESSION EXPIRATION
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_UPDATE_SECONDS = 10 * 60
# REST FRAMEWORK
#                   http://www.django-rest-framework.org/
REST_FRAMEWORK = {
    # hace la api solo accesible para admins
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}
# /REST FRAMEWORK

# GRAPHQL

GRAPHENE = {
    'SCHEMA': 'skyfolk.schema.schema'
}

# django-taggit
TAGGIT_CASE_INSENSITIVE = True

REDIS_PORT = 6379
REDIS_DB = 0
REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'localhost')

# cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{redis_host}:6379/1'.format(redis_host=REDIS_HOST),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'redis-cache':
        {
            'TIMEOUT': 3600,
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{redis_host}:6379/12".format(redis_host=REDIS_HOST),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "MAX_ENTRIES": 5000,
            }
        },
    'django_th':
        {
            'TIMEOUT': 3600,
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{redis_host}:6379/13".format(redis_host=REDIS_HOST),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "MAX_ENTRIES": 5000,
            }
        },
    'collectfast':
        {
            'TIMEOUT': 3600,
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{redis_host}:6379/2".format(redis_host=REDIS_HOST),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "MAX_ENTRIES": 5000,
            }
        },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

USER_ONLINE_TIMEOUT = 300
USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7

# CACHE BACK_IMAGE
BACK_IMAGE_CACHE_TIMEOUT = 300
BACK_IMAGE_DEFAULT_SIZE = 1024 * 1024 * 30
VIDEO_EXTENTIONS = ["avi", "mp4"]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'user_profile.middleware.ActiveUserMiddleware',
    'skyfolk.middleware.AutoLogout',
    'corsheaders.middleware.CorsMiddleware',
]

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
EL_PAGINATION_PER_PAGE = 50

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
# TODO: Usar rabbitmq cuando se haya solucionado el problema de cierre de conexion...
# RABBIT_HOSTNAME = os.environ.get('RABBIT_PORT_5672_TCP', 'rabbit')

# rabbitmq_url = 'amqp://guest:guest@{rabbit_host}/%2F?heartbeat=15'.format(rabbit_host=RABBIT_HOSTNAME)

"""
CHANNEL_LAYERS = {
    "default": {
        'BACKEND': 'asgi_rabbitmq.RabbitmqChannelLayer',
        "CONFIG": {
            "url": rabbitmq_url
        },
        "ROUTING": "skyfolk.routing.channel_routing",
    },
}
"""

redis_host = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'localhost')

# Channel layer definitions
# http://channels.readthedocs.org/en/latest/deploying.html#setting-up-a-channel-backend
ASGI_APPLICATION = 'skyfolk.routing.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
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

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# collecfast == (collecstatic)

COLLECTFAST_CACHE = 'collectfast'
COLLECTFAST_THREADS = 4

# Media (uploads, ...)
# MEDIA_ROOT = os.path.join(os.path.join(BASE_DIR, 'skyfolk'), 'media')
# MEDIA_URL = '/media/'

# NOTIFICACIONES
''' Marca las notificaciones como borradas
    en vez de eliminarlas de la base de datos.'''
NOTIFICATIONS_SOFT_DELETE = True
''' Permite enviar datos arbitrarios en las notificaciones '''
NOTIFICATIONS_USE_JSONFIELD = True

ADMINS = (
    ('Adrian Carayol', 'adriancarayol@gmail.com'),
    ('lostcitizen', 'lostcitizen@gmail.com'),
)
# Para emails al recibir nuevo feedback

TELLME_FEEDBACK_EMAIL = 'lostcitizen@gmail.com'

MANAGERS = ADMINS
POSTMAN_AUTO_MODERATE_AS = True
# Manejamos los envios de emails nosotros
# con el modulo notifications
POSTMAN_DISABLE_USER_EMAILING = True

# HAYSTACK REALTIME SIGNAL
HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 100

ELASTIC_URL = os.environ.get('ELASTICSEARCH_URL', 'localhost')
# ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = 'django_elasticsearch_dsl.signals.RealTimeSignalProcessor'
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTIC_URL
    },
}

# LOGROS
BADGIFY_BATCH_SIZE = None

# WEBPACK
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'js/bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}

# CKEDITOR
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': 'auto',
    },
}

# LOGGING
SKYFOLK_LOG_PATH = os.getenv('SKYFOLK_LOG_PATH', os.path.join(BASE_DIR, 'skyfolk.log'))


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
                '%(asctime)s %(levelname)s %(module)s %(process)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SKYFOLK_LOG_PATH,
            'maxBytes': 61280,
            'backupCount': 3,
            'formatter': 'verbose',

        },
    },
    'loggers':
        {
            'django.request': {
                'handlers': ['mail_admins', 'file'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.security.DisallowedHost': {
                'handlers': ['null'],
                'propagate': False,
            },
            '': {
                'handlers': ['console', ],
                'level': 'INFO',
            }
        }
}

