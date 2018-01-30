from django.template.loader import render_to_string

from ....base import BaseDashboardPluginWidget

__all__ = (
    'BasePollWidget',
    'Poll1x1Widget',
)

# **********************************************************************
# *********************** Base Video widget plugin *********************
# **********************************************************************


class BasePollWidget(BaseDashboardPluginWidget):
    """Base video plugin widget."""

    media_css = (
        'css/dash_plugin_video.css',
    )

    def render(self, request=None):
        """Render."""
        context = {'plugin': self.plugin}
        return render_to_string('poll/render.html', context)

# **********************************************************************
# ************************** Specific widgets **************************
# **********************************************************************


class Poll1x1Widget(BasePollWidget):
    """Video plugin 1x1 widget."""

    plugin_uid = 'poll_1x1'