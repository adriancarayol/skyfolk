from ....base import plugin_widget_registry
from ....factory import plugin_widget_factory
from ....contrib.plugins.image.dash_widgets import BaseImageWidget
from ....contrib.plugins.memo.dash_widgets import (
    BaseMemoWidget,
    BaseTinyMCEMemoWidget,
)
from ....contrib.plugins.rss_feed.dash_widgets import BaseReadRSSFeedWidget
from ....contrib.plugins.video.dash_widgets import BaseVideoWidget
from ....contrib.plugins.weather.dash_widgets import BaseWeatherWidget
from ....contrib.plugins.service.dash_widgets import BaseTriggerWidget

from .dash_widgets import (
    URL1x1SkySpaceMainWidget,
    URL1x1SkySpaceShortcutWidget,
)

__title__ = 'dash.contrib.layouts.skyspace.dash_plugins'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2013-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'

# **************************************************************************
# **************************************************************************
# ************************** Registering the widgets ***********************
# **************************************************************************
# **************************************************************************

# **************************************************************************
# ******************* Registering widgets for Image plugin *****************
# **************************************************************************


main_sizes = (
    (1, 1),
)
plugin_widget_factory(BaseImageWidget,
                      'skyspace',
                      'main',
                      'image',
                      main_sizes)

# **************************************************************************
# ******************* Registering widgets for Memo plugin ******************
# **************************************************************************


main_sizes = (
    (1, 1),
)
shortcut_sizes = (
    (1, 1),
)
plugin_widget_factory(BaseMemoWidget,
                      'skyspace',
                      'main',
                      'memo',
                      main_sizes)
plugin_widget_factory(BaseMemoWidget,
                      'skyspace',
                      'shortcut',
                      'memo',
                      shortcut_sizes)

# **************************************************************************
# ************** Registering widgets for TinyMCEMemo plugin ****************
# **************************************************************************


main_sizes = (
    (1, 1),
)
plugin_widget_factory(BaseTinyMCEMemoWidget,
                      'skyspace',
                      'main',
                      'tinymce_memo',
                      main_sizes)

# **************************************************************************
# ******************* Registering widgets for RSS plugin *******************
# **************************************************************************


main_sizes = (
    (1, 1),
)
plugin_widget_factory(BaseReadRSSFeedWidget,
                      'skyspace',
                      'main',
                      'read_rss_feed',
                      main_sizes)

# **************************************************************************
# ******************* Registering the widgets for URL plugin ***************
# **************************************************************************


plugin_widget_registry.register(URL1x1SkySpaceMainWidget)
plugin_widget_registry.register(URL1x1SkySpaceShortcutWidget)

# **************************************************************************
# ***************** Registering the widgets for Video plugin ***************
# **************************************************************************


main_sizes = (
    (1, 1),
)
plugin_widget_factory(BaseVideoWidget,
                      'skyspace',
                      'main',
                      'video',
                      main_sizes)


# **************************************************************************
# ***************** Registering the widgets for Trigger plugin ***************
# **************************************************************************


main_sizes = (
    (1, 1),
)
plugin_widget_factory(BaseTriggerWidget,
                      'skyspace',
                      'main',
                      'trigger',
                      main_sizes)

# **************************************************************************
# *************** Registering the widgets for Weather plugin ***************
# **************************************************************************


# main_sizes = (
#    (1, 1),
#)
# plugin_widget_factory(BaseWeatherWidget,
 #                     'skyspace',
 #                     'main',
 #                    'weather',
 #                     main_sizes)
