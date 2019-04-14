from ....base import plugin_widget_registry
from ....factory import plugin_widget_factory
from ....contrib.plugins.image.dash_widgets import BaseImageWidget
from ....contrib.plugins.memo.dash_widgets import BaseMemoWidget, BaseTinyMCEMemoWidget
from ....contrib.plugins.rss_feed.dash_widgets import BaseReadRSSFeedWidget
from ....contrib.plugins.video.dash_widgets import BaseVideoWidget
from ....contrib.plugins.poll.dash_widgets import BasePollWidget
from ....contrib.plugins.statistics.dash_widgets import BaseStatisticsWidget
from ....contrib.plugins.follows.dash_widgets import BaseFollowsWidget
from ....contrib.plugins.twitch.dash_widgets import BaseTwitchWidget
from ....contrib.plugins.service.dash_widgets import BaseServiceWidget

from .dash_widgets import URL1x1ProfileMainWidget

# **************************************************************************
# **************************************************************************
# ************************** Registering the widgets ***********************
# **************************************************************************
# **************************************************************************

# **************************************************************************
# ******************* Registering widgets for Image plugin *****************
# **************************************************************************


main_sizes = ((1, 1),)
plugin_widget_factory(BaseImageWidget, "profile", "main", "image", main_sizes)

# **************************************************************************
# ******************* Registering widgets for Memo plugin ******************
# **************************************************************************


main_sizes = ((1, 1),)

plugin_widget_factory(BaseMemoWidget, "profile", "main", "memo", main_sizes)

# **************************************************************************
# ************** Registering widgets for TinyMCEMemo plugin ****************
# **************************************************************************


main_sizes = ((1, 1),)
plugin_widget_factory(
    BaseTinyMCEMemoWidget, "profile", "main", "tinymce_memo", main_sizes
)

# **************************************************************************
# ******************* Registering widgets for RSS plugin *******************
# **************************************************************************


main_sizes = ((1, 1),)
plugin_widget_factory(
    BaseReadRSSFeedWidget, "profile", "main", "read_rss_feed", main_sizes
)

# **************************************************************************
# ******************* Registering the widgets for URL plugin ***************
# **************************************************************************


plugin_widget_registry.register(URL1x1ProfileMainWidget)

# **************************************************************************
# ***************** Registering the widgets for Video plugin ***************
# **************************************************************************


main_sizes = ((1, 1),)
plugin_widget_factory(BaseVideoWidget, "profile", "main", "video", main_sizes)


# **************************************************************************
# ***************** Registering the widgets for Poll plugin ***************
# **************************************************************************


main_sizes = ((1, 1),)

plugin_widget_factory(BasePollWidget, "profile", "main", "poll", main_sizes)

# *************************************************************************
# ************** Registering the widgets for Statistics plugin ***********
# ***********************************************************************
main_sizes = ((1, 1),)

plugin_widget_factory(BaseStatisticsWidget, "profile", "main", "statistics", main_sizes)

plugin_widget_factory(BaseFollowsWidget, "profile", "main", "follows", main_sizes)

plugin_widget_factory(BaseTwitchWidget, "profile", "main", "twitch", main_sizes)

plugin_widget_factory(BaseServiceWidget, "profile", "main", "service", main_sizes)
