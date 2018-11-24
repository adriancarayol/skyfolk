from django.utils.translation import ugettext_lazy as _

from ....base import BaseDashboardPlugin
from ....factory import plugin_factory
from .forms import ServiceForm


# ****************************************************************************
# ******************************* Base memo plugin ***************************
# ****************************************************************************


class BaseServicePlugin(BaseDashboardPlugin):
    """Base memo plugin."""

    name = _("Red social")
    group = _("Redes sociales")
    form = ServiceForm


# ****************************************************************************
# ********** Generating and registering the plugins using factory ************
# ****************************************************************************

sizes = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6)
)

plugin_factory(BaseServicePlugin, 'service', sizes)
