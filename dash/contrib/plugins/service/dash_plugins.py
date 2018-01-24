from django.utils.translation import ugettext_lazy as _

from ....base import BaseDashboardPlugin
from ....factory import plugin_factory

from .forms import TriggerForm
from dash_services.models import TriggerService

# ****************************************************************************
# ********************************* Service plugin *******************************
# ****************************************************************************


class BaseTriggerPlugin(BaseDashboardPlugin):
    """Base Trigger plugin."""

    def __init__(self, layout_uid, placeholder_uid, workspace=None, user=None, position=None):
        super(BaseTriggerPlugin, self).__init__(layout_uid=layout_uid, placeholder_uid=placeholder_uid,
                                                workspace=workspace,
                                                user=user, position=position)

    name = _("Trigger")
    group = _("Internet")
    form = TriggerForm

    @property
    def html_class(self):
        """HTML class.

        If plugin has an image, we add a class ``iconic`` to it.
        """
        html_class = super(BaseTriggerPlugin, self).html_class
        return html_class

    def update_plugin_data(self, dashboard_entry):
        """Update plugin data.

        Should return a dictionary with the plugin data which is supposed to
        be updated.
        """
        try:
            trigger = TriggerService.objects.get(pk=self.data.trigger)
        except TriggerService.DoesNotExist:
            return

        if trigger:
            data = {
                'trigger': trigger.pk,
                'description': trigger.description,
                'result': trigger.result,
            }

            return data

# ****************************************************************************
# ********** Generating and registering the Trigger plugins using factory ********
# ****************************************************************************


sizes = (
    (1, 1),
    (2, 2)
)

plugin_factory(BaseTriggerPlugin, 'trigger', sizes)
