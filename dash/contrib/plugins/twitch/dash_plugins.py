from django.utils.translation import ugettext_lazy as _
from ....base import BaseDashboardPlugin
from ....factory import plugin_factory

from .forms import TwitchForm

# ***************************************************************************
# ******************************* Base Video plugin *************************
# ***************************************************************************


class BaseTwitchPlugin(BaseDashboardPlugin):
    """Base Video plugin."""

    name = _("Twitch")
    group = _("Internet")
    form = TwitchForm
    html_classes = []

# ***************************************************************************
# ********** Generating and registering the plugins using factory ***********
# ***************************************************************************


sizes = (
    (1, 1),
)

plugin_factory(BaseTwitchPlugin, 'twitch', sizes)
