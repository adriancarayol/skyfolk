from django.template.loader import render_to_string
from publications.models import Publication
from user_profile.models import LikeProfile
from ....base import BaseDashboardPluginWidget

__title__ = 'dash.contrib.plugins.follows.dash_widgets'

__all__ = (
    'BaseStatisticsWidget',
    'Statistics1x1Widget',
    'Statistics2x2Widget',
)

# **********************************************************************
# ************************* Base Statistics widget plugin *********************
# **********************************************************************


class BaseStatisticsWidget(BaseDashboardPluginWidget):
    """Statistics plugin widget."""

    def render(self, request=None):
        """Render."""
        user = self.plugin.user
        total_publications = Publication.objects.get_publications_by_author(user).count()
        total_likes = LikeProfile.objects.filter(from_profile=user.profile).count()
        context = {
            'plugin': self.plugin,
            'total_publications': total_publications,
            'total_likes': total_likes
        }
        return render_to_string('statistics/render.html', context)

# **********************************************************************
# ************************** Specific widgets **************************
# **********************************************************************


class Statistics1x1Widget(BaseStatisticsWidget):
    """follows plugin 1x1 widget."""

    plugin_uid = 'statistics_1x1'


class Statistics2x2Widget(BaseStatisticsWidget):
    """Statistics plugin 2x2 widget."""

    plugin_uid = 'statistics_2x2'
    cols = 2
    rows = 2
