import numpy as np
from django.template.loader import render_to_string
from ....base import BaseDashboardPluginWidget
from ....models import DashboardEntry

__all__ = (
    'BaseTwitchWidget',
    'Twitch1x1Widget',
)


# **********************************************************************
# *********************** Base Video widget plugin *********************
# **********************************************************************


class BaseTwitchWidget(BaseDashboardPluginWidget):
    """Base video plugin widget."""

    # media_css = (
    #     'css/dash_plugin_video.css',
    # )

    media_js = (
        'js/dash_plugin_poll.js',
        'js/Chart.bundle.min.js',
    )

    def render(self, request=None):
        context = {'plugin': self.plugin}
        return render_to_string('twitch/render.html', context)


# **********************************************************************
# ************************** Specific widgets **************************
# **********************************************************************


class Twitch1x1Widget(BaseTwitchWidget):
    """Video plugin 1x1 widget."""

    plugin_uid = 'twitch_1x1'
