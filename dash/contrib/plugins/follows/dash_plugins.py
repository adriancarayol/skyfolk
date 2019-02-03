from django.utils.translation import ugettext_lazy as _

from ....base import BaseDashboardPlugin
from ....factory import plugin_factory

from .forms import FollowsForm

__all__ = ('BaseFollowsPlugin',)


# ****************************************************************************
# ********************************* FOLLOWS plugin *******************************
# ****************************************************************************


class BaseFollowsPlugin(BaseDashboardPlugin):
    """Base Statistics plugin."""

    name = _("Cuentas que sigo")
    group = _("Perfil")
    form = FollowsForm


    @property
    def html_class(self):
        """HTML class.

        If plugin has an image, we add a class ``iconic`` to it.
        """
        html_class = super(BaseFollowsPlugin, self).html_class
        return html_class

# ****************************************************************************
# ********** Generating and registering the FOLLOWS plugins using factory ********
# ****************************************************************************


sizes = (
    (1, 1),
    (2, 2)
)

plugin_factory(BaseFollowsPlugin, 'follows', sizes)
