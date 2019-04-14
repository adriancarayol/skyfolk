import os
from django.core.exceptions import ImproperlyConfigured
from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS += ["127.0.0.1"]
SECRET_KEY = os.environ.get("SECRET_KEY", "NO-SECRET")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_ENV_DB", "skyfolk_pre_db"),
        "USER": os.environ.get("DB_ENV_POSTGRES_USER", "skyfolk_pre"),
        "PASSWORD": os.environ.get("DB_ENV_POSTGRES_PASSWORD", "skyf0lk_p4ssword@"),
        "HOST": os.environ.get("DB_PORT_5432_TCP_ADDR", "localhost"),
        "PORT": os.environ.get("DB_PORT_5432_TCP_PORT", "5432"),
    }
}

# ACCOUNT SETTINGS FOR PRE
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/skyfolk.net/run/static/static/"
MEDIA_ROOT = "/var/www/skyfolk.net/run/static/media/"
MEDIA_URL = "/media/"
# INVITATIONS ONLY EMAIL
INVITATIONS_INVITATION_ONLY = False

# ELASTICSEARCH CONFIGURATION
ELASTIC_URL = os.environ.get("ELASTICSEARCH_URL", "localhost")

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
#         'URL': 'http://{elastic_host}:9200/'.format(elastic_host=ELASTIC_URL),
#         'INDEX_NAME': 'haystack',
#     },
# }
