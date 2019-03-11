import numpy as np
from django.template.loader import render_to_string
from dash.contrib.plugins.poll.models import PollResponse
from ....base import BaseDashboardPluginWidget
from .forms import PollResponseForm
from ....models import DashboardEntry

__all__ = (
    'BasePollWidget',
    'Poll1x1Widget',
)


# **********************************************************************
# *********************** Base Video widget plugin *********************
# **********************************************************************


class BasePollWidget(BaseDashboardPluginWidget):
    """Base video plugin widget."""

    # media_css = (
    #     'css/dash_plugin_video.css',
    # )

    media_js = (
        'js/dash_plugin_poll.js',
        'js/Chart.bundle.min.js',
    )

    def render(self, request=None):
        """Render."""
        from_path = None

        if request:
            path = request.path
            path = path.split('/')

            if path and len(path) > 1:
                from_path = path[1]
        
        is_profile = False

        if from_path == 'profile':
            is_profile = True

        poll = DashboardEntry.objects.get(workspace=self.plugin.workspace, plugin_uid=self.plugin_uid,
                                          position=self.plugin.position, layout_uid=self.layout_uid)
        form = PollResponseForm(initial={'pk': poll.id})
        poll_responses = PollResponse.objects.filter(poll=poll).values_list('options', flat=True)
        responses = {
            'no': np.size(poll_responses) - np.count_nonzero(poll_responses),
            'si': np.count_nonzero(poll_responses)
        }
        context = {'plugin': self.plugin, 'form': form, 'responses': responses, 'is_profile': is_profile}
        return render_to_string('poll/render.html', context, request=self.plugin.request)


# **********************************************************************
# ************************** Specific widgets **************************
# **********************************************************************


class Poll1x1Widget(BasePollWidget):
    """Video plugin 1x1 widget."""

    plugin_uid = 'encuesta_1x1'
