try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = 'dash.contrib.plugins.twitch'
        label = 'dash_contrib_plugins_twitch'

except ImportError:
    pass