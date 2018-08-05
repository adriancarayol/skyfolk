from ....contrib.plugins.url.dash_widgets import (
    BaseBookmarkWidget,
    URL1x1Widget,
)

__title__ = 'dash.contrib.layouts.skyspace.dash_widgets'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2013-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'URL1x1SkySpaceMainWidget',
    'URL1x1SkySpaceShortcutWidget',
)

# *********************************************************
# *********************************************************
# *********************** URL widgets *********************
# *********************************************************
# *********************************************************


class URL1x1SkySpaceMainWidget(URL1x1Widget):
    """URL plugin widget for SkySpace layout (placeholder `main`)."""

    layout_uid = 'skyspace'
    placeholder_uid = 'main'
    media_css = (
        'css/dash_plugin_url_skyspace.css',
    )


class URL1x1SkySpaceShortcutWidget(URL1x1SkySpaceMainWidget):
    """URL plugin widget for SkySpace layout (placeholder `shortcuts`)."""

    placeholder_uid = 'shortcuts'
