from django.template.loader import render_to_string

from ....base import BaseDashboardPluginWidget
from ....models import DashboardEntry

__all__ = (
    'BaseServiceWidget',
    'Service1x1Widget',
    'Service2x2Widget',
    'Service3x3Widget',
    'Service4x5Widget',
    'Service5x5Widget',
    'Service6x6Widget',
)


# ***********************************************************************
# ********************** Base widget for Memo plugin ********************
# ***********************************************************************


class BaseServiceWidget(BaseDashboardPluginWidget):
    """Base service plugin widget."""

    def render(self, request=None):
        """Render."""
        # TODO: Optimize this, get entry id directly.
        entry = DashboardEntry._default_manager \
            .filter(user=self.plugin.user,
                    layout_uid=self.plugin.layout_uid,
                    position=self.plugin.position,
                    workspace=self.plugin.workspace).first()
        context = {'plugin': self.plugin, 'id': entry.pk}
        return render_to_string('service/render.html', context)


# ***********************************************************************
# ********************** Specific widgets for Memo plugin ***************
# ***********************************************************************


class Service1x1Widget(BaseServiceWidget):
    """Service 1x1 plugin widget."""

    plugin_uid = 'service_1x1'
    cols = 1
    rows = 1


class Service2x2Widget(BaseServiceWidget):
    """Service 2x2 plugin widget."""

    plugin_uid = 'service_2x2'
    cols = 2
    rows = 2


class Service3x3Widget(BaseServiceWidget):
    """Service 3x3 plugin widget."""

    plugin_uid = 'service_3x3'
    cols = 3
    rows = 3


class Service4x5Widget(BaseServiceWidget):
    """Service 4x5 plugin widget."""

    plugin_uid = 'service_4x5'
    cols = 4
    rows = 5


class Service5x5Widget(BaseServiceWidget):
    """Service 5x5 plugin widget."""

    plugin_uid = 'service_5x5'
    cols = 5
    rows = 5


class Service6x6Widget(BaseServiceWidget):
    """Service 6x6 plugin widget."""

    plugin_uid = 'service_6x6'
    cols = 6
    rows = 6
