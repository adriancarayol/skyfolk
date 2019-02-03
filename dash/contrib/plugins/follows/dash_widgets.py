from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from user_profile.models import RelationShipProfile, FOLLOWING
from ....base import BaseDashboardPluginWidget

__title__ = 'dash.contrib.plugins.follows.dash_widgets'

__all__ = (
    'BaseFollowsWidget',
    'Follows1x1Widget',
    'Follows2x2Widget',
)


# **********************************************************************
# ************************* Base Statistics widget plugin *********************
# **********************************************************************


class BaseFollowsWidget(BaseDashboardPluginWidget):
    """Statistics plugin widget."""

    def render(self, request=None):
        """Render."""
        user = self.plugin.user
        follows = RelationShipProfile.objects.filter(
            from_profile__user=user, type=FOLLOWING
        ).select_related("to_profile", "to_profile__user").prefetch_related("to_profile__tags")
        paginator = Paginator(follows, 25)
        page = 1

        try:
            following = paginator.page(page)
        except PageNotAnInteger:
            following = paginator.page(1)
        except EmptyPage:
            following = paginator.page(paginator.num_pages)

        context = {
            'plugin': self.plugin,
            'friends_top12': following,
        }
        return render_to_string('follows/render.html', context)


# **********************************************************************
# ************************** Specific widgets **************************
# **********************************************************************


class Follows1x1Widget(BaseFollowsWidget):
    """follows plugin 1x1 widget."""

    plugin_uid = 'follows_1x1'


class Follows2x2Widget(BaseFollowsWidget):
    """Follows plugin 2x2 widget."""

    plugin_uid = 'follows_2x2'
    cols = 2
    rows = 2
