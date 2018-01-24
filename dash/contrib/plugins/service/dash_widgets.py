from django.template.loader import render_to_string
from dash_services.models import TriggerService
from th_rss.models import Rss
from django.core.cache import caches
from ....base import BaseDashboardPluginWidget

__all__ = (
    'BaseTriggerWidget',
    'Trigger1x1Widget',
    'Trigger2x2Widget',
)

# **********************************************************************
# ************************* Base URL widget plugin *********************
# **********************************************************************


class BaseTriggerWidget(BaseDashboardPluginWidget):
    """Trigger plugin widget."""

    def render(self, request=None):
        """Render."""
        trigger = TriggerService.objects.get(pk=self.plugin.data.trigger)
        provider = trigger.provider.name.name.split('Service')[1].lower()
        rss = Rss.objects.get(trigger_id=self.plugin.data.trigger)
        cache = caches['django_th']
        pattern = 'th_{provider}_{id}'.format(provider=provider,
                                                  id=rss.trigger_id)
        context = {'plugin': self.plugin, 'results': cache.get(pattern)}
        return render_to_string('service/render.html', context)

# **********************************************************************
# ************************** Specific widgets **************************
# **********************************************************************


class Trigger1x1Widget(BaseTriggerWidget):
    """URL plugin 1x1 widget."""

    plugin_uid = 'trigger_1x1'
    cols = 1
    rows = 1


class Trigger2x2Widget(BaseTriggerWidget):
    """URL plugin 2x2 widget."""

    plugin_uid = 'trigger_2x2'
    cols = 2
    rows = 2
