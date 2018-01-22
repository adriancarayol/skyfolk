try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = 'dash.contrib.layouts.profile'
        label = 'dash_contrib_layouts_profile'

except ImportError:
    pass

__title__ = 'dash.contrib.layouts.profile.apps'