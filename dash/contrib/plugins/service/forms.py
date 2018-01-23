from django import forms
from django.utils.translation import ugettext_lazy as _

from ....base import DashboardPluginFormBase
from skyfolk.models import TriggerService

__all__ = (
    'TriggerForm',
)

class TriggerForm(forms.Form, DashboardPluginFormBase):
    class Media(object):
        """Media."""

        css = {
            'all': ('css/dash_plugin_service_form.css',)
        }
        js = ('js/dash_plugin_service_form.js',)

    plugin_data_fields = [
        ("trigger", ""),
        ("result", ""),
        ("description", ""),
    ]

    trigger = forms.ModelChoiceField(label=_("Trigger"),
                                     queryset=TriggerService.objects.all(),
                                     empty_label=_('---------'),
                                     required=True)

    def save_plugin_data(self, request=None):
        """Save plugin data.

        Saving the plugin data and moving the file.
        """
        trigger = self.cleaned_data.get('trigger', None)
        if trigger:
            # Since it's a ``ModelChoiceField``, we can safely given an ID.
            self.cleaned_data['trigger'] = trigger.pk

            # Saving the rest of the fields.
            self.cleaned_data['result'] = trigger.result
            self.cleaned_data['description'] = trigger.description