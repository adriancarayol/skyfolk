"""
ASGI entrypoint file for default channel layer.

Points to the channel layer configured as "default" so you can point
ASGI applications at "liveblog.asgi:channel_layer" as their channel layer.
"""

import os
import django
from channels.routing import get_default_application


def get_env_variable(var_name):
    """Intenta leer una variable de entorno"""
    try:
        return os.environ[var_name]
    except KeyError:
        return "develop"
        # error_msg = "Set the %s environment variable" % (var_name)
        # raise ImproperlyConfigured(error_msg)


DAPHNE_RUNLEVEL = get_env_variable("DAPHNE_RUNLEVEL")
if DAPHNE_RUNLEVEL == "master":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfolk.settings.master")
elif DAPHNE_RUNLEVEL == "pre":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfolk.settings.pre")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfolk.settings.develop")

django.setup()
application = get_default_application()
