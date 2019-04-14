try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = "dash.contrib.plugins.follows"
        label = "dash_contrib_plugins_follows"


except ImportError:
    pass
