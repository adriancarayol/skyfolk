from ....base import plugin_widget_registry
from ....factory import plugin_widget_factory
from ....contrib.plugins.dummy.dash_widgets import BaseDummyWidget
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
    URL1x1ProfileMainWidget,
)

# **************************************************************************
# **************************************************************************
# ************************** Registering the widgets ***********************
# **************************************************************************
# **************************************************************************

# **************************************************************************
# ******************* Registering widgets for Dummy plugin *****************
# **************************************************************************


main_sizes = (
    (1, 1),
    (1, 2),
    (2, 1),
    (3, 3),
)

plugin_widget_factory(BaseDummyWidget,
                      'profile',
                      'main',
                      'dummy',
                      main_sizes)

# **************************************************************************
# ******************* Registering widgets for Image plugin *****************
# **************************************************************************


main_sizes = (
    (1, 1),
    (2, 2),
    (2, 3),
    (3, 2),
    (3, 3),
)
plugin_widget_factory(BaseImageWidget,
                      'profile',
                      'main',
                      'image',
                      main_sizes)

# **************************************************************************
# ******************* Registering widgets for Memo plugin ******************
# **************************************************************************


main_sizes = (
    (2, 2),
    (3, 3),
    (4, 5),
)

plugin_widget_factory(BaseMemoWidget,
                      'profile',
                      'main',
                      'memo',
                      main_sizes)

# **************************************************************************
# ************** Registering widgets for TinyMCEMemo plugin ****************
# **************************************************************************


main_sizes = (
    (2, 2),
    (3, 3),
)
plugin_widget_factory(BaseTinyMCEMemoWidget,
                      'profile',
                      'main',
                      'tinymce_memo',
                      main_sizes)

# **************************************************************************
# ******************* Registering widgets for RSS plugin *******************
# **************************************************************************


main_sizes = (
    (2, 3),
    (3, 3),
)
plugin_widget_factory(BaseReadRSSFeedWidget,
                      'profile',
                      'main',
                      'read_rss_feed',
                      main_sizes)

# **************************************************************************
# ******************* Registering the widgets for URL plugin ***************
# **************************************************************************


plugin_widget_registry.register(URL1x1ProfileMainWidget)

# **************************************************************************
# ***************** Registering the widgets for Video plugin ***************
# **************************************************************************


main_sizes = (
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)
plugin_widget_factory(BaseVideoWidget,
                      'profile',
                      'main',
                      'video',
                      main_sizes)

# **************************************************************************
# *************** Registering the widgets for Weather plugin ***************
# **************************************************************************


main_sizes = (
    (2, 2),
    (3, 3),
)
plugin_widget_factory(BaseWeatherWidget,
                      'profile',
                      'main',
                      'weather',
                      main_sizes)

# **************************************************************************
# ***************** Registering the widgets for Trigger plugin ***************
# **************************************************************************


main_sizes = (
    (1, 1),
    (2, 2),
)

plugin_widget_factory(BaseTriggerWidget,
                      'profile',
                      'main',
                      'trigger',
                      main_sizes)