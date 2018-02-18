try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = 'dash.contrib.plugins.poll'
        label = 'dash_contrib_plugins_poll'

except ImportError:
    pass