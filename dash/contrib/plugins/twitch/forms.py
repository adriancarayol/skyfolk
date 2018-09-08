from django import forms
from django.utils.translation import ugettext_lazy as _
from ....base import DashboardPluginFormBase

__all__ = ('TwitchForm',)


class TwitchForm(forms.Form, DashboardPluginFormBase):
    """Poll form for ``PollPlugin`` plugin."""

    plugin_data_fields = [
        ("channel", ""),
        ("description", ""),
    ]

    channel = forms.CharField(label=_("Channel"), required=True, max_length=100)
    description = forms.CharField(label=_("Description"), required=True, max_length=200)
