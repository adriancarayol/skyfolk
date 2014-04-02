#encoding:utf-8
"""
Django settings for skyfolk project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from django.conf import settings
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Identificando la ruta del proyecto
import os
RUTA_PROYECTO = os.path.dirname(os.path.realpath(__file__))

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
#    'south',		# Gestiona las migraciones de bdd
	'userena',		# Gestiona las cuentas de usuario
	'guardian',		# Dependencia de userena
	'easy_thumbnails',	# Dependencia de userena
	'rest_framework',	# REST framework
)

# Local Applications
LOCAL_APPS = (
	'principal',
	'accounts',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

##########################################################################
# Userena - módulo de cuentas de usuario
# 20140316 - Instalación
##########################################################################
# Guardian (Userena dependecy)
#
AUTHENTICATION_BACKENDS = (
	'userena.backends.UserenaAuthenticationBackend',
	'guardian.backends.ObjectPermissionBackend',
	'django.contrib.auth.backends.ModelBackend',
)
ANONYMOUS_USER_ID = -1

# USERENA Django Settings: http://django-userena.readthedocs.org/en/latest/settings.html#django-settings
#
LOGIN_URL = '/accounts/signin/'										# Define la url para hacer login
LOGOUT_URL = '/accounts/signout/'										# Define la url para hacer logout
LOGIN_REDIRECT_URL = '/accounts/%(username)s/'						# Url a la que redirigir después de hacer login
AUTH_PROFILE_MODULE = 'accounts.MyProfile'						# Módulo/app con modelo de datos del usuario

# USERENA Settings: http://django-userena.readthedocs.org/en/latest/settings.html
#
#USERENA_SIGNIN_AFTER_SIGNUP = False								# Define si es necesario logarse después de registrarse: http://django-userena.readthedocs.org/en/latest/settings.html
#USERENA_SIGNIN_REDIRECT_URL = '/accounts/%(username)s/'			# Define la url a la que redirigir después de hacer login. Por defecto: '/accounts/%(username)s/'
USERENA_ACTIVATION_REQUIRED = False									# Define si se requiere activar la cuenta
USERENA_ACTIVATION_DAYS = 7											# Días para activar la cuenta
#USERENA_ACTIVATION_NOTIFY = False									# Define si se enviara o no una notificación de cuando acaba el plazo para activar la cuenta
#USERENA_ACTIVATION_NOTIFY_DAYS = 2									# Dias antes de enviar la notificación de aviso de expiración de cuenta por la no activación
USERENA_ACTIVATED = True											# String that defines the value that the activation_key will be set to after a successful signup.
USERENA_REMEMBER_ME_DAYS = (gettext('a month'), 30)					# Los días que el usuario puede escoger ser recordado (cuanto tiempo permanecerá abierta la sesión)
#USERENA_FORBIDDEN_USERNAMES = ('activate','me')					# Define los nombre de usuarios prohibidos
#USERENA_MUGSHOT_GRAVATAR = True									# Define si se buscará un avatar en Gravatar si el usuario no sube un avatar
#USERENA_MUGSHOT_GRAVATAR_SECURE = USERENA_USE_HTTPS				# Define si la conexión a Gravatar será por https
#USERENA_MUGSHOT_DEFAULT = 'http://wwww.1.com/imagen.png'			# Define un avatar por defecto cuando el usuario no ha subido su avatar
#USERENA_MUGSHOT_SIZE = 200											# Dimensiones en pixels del tamaño de la imagenes (cuadrada)
#USERENA_MUGSHOT_PATH = 'mugshots/%(username)s/'					# Define donde se subirán los avatares (append a MEDIA_PATH)
#USERENA_USE_HTTPS = True											# Habilitar si el sitio usa https
#USERENA_DEFAULT_PRIVACY = 'closed'									# Define la privacidad por defecto del perfil de usuario: closed,registered,open
#USERENA_PROFILE_DETAIL_TEMPLATE = 'userena/profile_detail.html'	# Url del template a usar para los perfiles de usuario
#USERENA_PROFILE_LIST_TEMPLATE = 'userena/profile_list.html'		# Url del template a usar para listar todos los usuarios
#USERENA_DISABLE_PROFILE_LIST = False								# Des/habilita la función de listar todos los usuarios
#USERENA_DISABLE_SIGNUP = False										# Deshabilita el registro de nuevos usuarios
#USERENA_USE_MESSAGES = True										# Define si Userena debe utilizar el framework de mensajes de django para notificar al usuario de cualquier cambio
#USERENA_LANGUAGE_FIELD = 'languaje'								# Define el campo de idioma para perfiles con idioma personalizado
USERENA_WITHOUT_USERNAMES = False									# Deshabilita la identificación por nombre de usuario (usa email)
#USERENA_HIDE_EMAIL = True											# Previene que se muestren las direcciones de correo a otras personas
#USERENA_HTML_EMAIL = False											# Define si los emails serán generados usando un template html
#USERENA_USE_PLAIN_TEMPLATE = True									# Define si los emails serán generados usando texto plano
#
# /Userena - config módulo de cuentas

##########################################################################
# Configuración servidor SMTP envio de correos
# 20140316 - Instalación
##########################################################################
#					https://docs.djangoproject.com/en/dev/topics/email/
#
# cuenta test de gmail para el envío de mails
# user: dfgsdfgsdf906@gmail.com
# pass: 56g4eD&%&FGfgdsf
#
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'dfgsdfgsdf906@gmail.com'
EMAIL_HOST_PASSWORD = '56g4eD&%&FGfgdsf'

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
#					http://www.django-rest-framework.org/
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
			'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': 'skyfolk_db',                      # Or path to database file if using sqlite3.
			# The following settings are not used with sqlite3:
			'USER': 'postgres',
			'PASSWORD': 'Palindromos_720',
			'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
			'PORT': '',                      # Set to empty string for default.
		}
	}

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


# Identificador
SITE_ID=1

ADMINS = (
	#('Adrian Carayol', 'adriancarayol@gmail.com'),
	#('Ionut Remires', ' ... '),     # email?
	#('Pablo Rossiñol', ' ... ' )    # email?
	('Carlos Canicio', 'canicio7@gmail.com'),
	('Lostcitizen', 'lostcitizen@gmail.com'),
)

TEMPLATE_DIRS = (
	os.path.join(RUTA_PROYECTO,'plantillas'),
)

STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(RUTA_PROYECTO,'static'),
)

#...................................................................

## heroku
#
#>>>>>>> 4e51631da3d58553e711f24ffe5daad5b50bacd2
## Parse database configuration from $DATABASE_URL
#import dj_database_url
#DATABASES['default'] =  dj_database_url.config()
## Honor the 'X-Forwarded-Proto' header for request.is_secure()
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
## Allow all host headers
#ALLOWED_HOSTS = ['*']
## Static asset configuration
#import os
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#STATIC_ROOT = 'staticfiles'
#STATIC_URL = '/static/'
#
#STATICFILES_DIRS = (
#    os.path.join(BASE_DIR, 'static'),
#)
#
##..................................................................
