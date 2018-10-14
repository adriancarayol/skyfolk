from django import forms
from django.utils.translation import ugettext_lazy as _

from ....base import DashboardPluginFormBase



class ServiceForm(forms.Form, DashboardPluginFormBase):
    """Servie form (for ``Service`` plugin)."""

    plugin_data_fields = [
        ("title", ""),
        ("text", ""),
        ("service", "")
    ]

    title = forms.CharField(label=_("Title"), required=False)
    service = forms.CharField(label=_("Service"), required=True)
    text = forms.CharField(label=_("Text"), required=True,
                           widget=forms.widgets.Textarea(attrs={"class": "materialize-textarea"}))