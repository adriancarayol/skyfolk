from django import forms
from django.utils.translation import ugettext_lazy as _
from external_services.models import UserService
from ....base import DashboardPluginFormBase


class ServiceForm(forms.Form, DashboardPluginFormBase):
    """Servie form (for ``Service`` plugin)."""

    plugin_data_fields = [
        ("title", ""),
        ("text", ""),
        ("service", "")
    ]

    service = forms.ModelChoiceField(queryset=UserService.objects.filter(service__status=True),
                                     required=True)
    text = forms.CharField(label=_("Text"), required=True,
                           widget=forms.widgets.Textarea(attrs={"class": "materialize-textarea"}))

    def save_plugin_data(self, request=None):
        service = self.cleaned_data.get('service', None)

        if service:
            self.cleaned_data['service'] = service.pk
            self.cleaned_data['title'] = service.service.name
