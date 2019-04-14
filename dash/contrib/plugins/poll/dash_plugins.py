from django.utils.translation import ugettext_lazy as _
from ....base import BaseDashboardPlugin
from ....factory import plugin_factory

from .forms import PollForm

# ***************************************************************************
# ******************************* Base Video plugin *************************
# ***************************************************************************


class BasePollPlugin(BaseDashboardPlugin):
    """Base Video plugin."""

    name = _("Encuesta")
    group = _("Encuestas")
    form = PollForm
    html_classes = []


# ***************************************************************************
# ********** Generating and registering the plugins using factory ***********
# ***************************************************************************


sizes = ((1, 1),)

plugin_factory(BasePollPlugin, "poll", sizes)
