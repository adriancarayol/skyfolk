from django.utils.translation import ugettext_lazy as _

from ....base import BaseDashboardPlugin
from ....factory import plugin_factory

from .forms import StatisticsForm

__all__ = ("BaseStatisticsPlugin",)


# ****************************************************************************
# ********************************* STATISTICS plugin *******************************
# ****************************************************************************


class BaseStatisticsPlugin(BaseDashboardPlugin):
    """Base Statistics plugin."""

    name = _("Estadisticas de mi perfil")
    group = _("Perfil")
    form = StatisticsForm

    @property
    def html_class(self):
        """HTML class.

        If plugin has an image, we add a class ``iconic`` to it.
        """
        html_class = super(BaseStatisticsPlugin, self).html_class
        return html_class


# ****************************************************************************
# ********** Generating and registering the STATISTICS plugins using factory ********
# ****************************************************************************


sizes = ((1, 1), (2, 2))

plugin_factory(BaseStatisticsPlugin, "statistics", sizes)
