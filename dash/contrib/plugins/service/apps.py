try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = "dash.contrib.plugins.service"
        label = "dash_contrib_plugins_service"


except ImportError:
    pass
