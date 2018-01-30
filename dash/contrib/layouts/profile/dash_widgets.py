from ....contrib.plugins.url.dash_widgets import (
    URL1x1Widget,
)

__all__ = (
    'URL1x1ProfileMainWidget',
)

# *********************************************************
# *********************************************************
# *********************** URL widgets *********************
# *********************************************************
# *********************************************************


class URL1x1ProfileMainWidget(URL1x1Widget):
    """URL plugin widget for Android layout (placeholder `main`)."""

    layout_uid = 'profile'
    placeholder_uid = 'main'
    media_css = (
        'css/dash_plugin_url_android.css',
    )
