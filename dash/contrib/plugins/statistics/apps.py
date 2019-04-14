try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = "dash.contrib.plugins.statistics"
        label = "dash_contrib_plugins_statistics"


except ImportError:
    pass
