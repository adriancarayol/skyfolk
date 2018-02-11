from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import PollResponse
from ....base import DashboardPluginFormBase

__all__ = ('PollForm',)


class PollForm(forms.Form, DashboardPluginFormBase):
    """Poll form for ``PollPlugin`` plugin."""

    plugin_data_fields = [
        ("title", ""),
        ("description", ""),
    ]

    title = forms.CharField(label=_("Title"), required=True, max_length=100)
    description = forms.CharField(label=_("Description"), required=True, max_length=200)


class PollResponseForm(forms.Form):
    pk = forms.IntegerField(required=True, widget=forms.HiddenInput())
