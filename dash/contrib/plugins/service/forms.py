from django import forms
from external_services.models import UserService
from external_services.factory import ServiceFormFactory
from ....base import DashboardPluginFormBase


class ServiceForm(forms.Form, DashboardPluginFormBase):
    """Servie form (for ``Service`` plugin)."""

    plugin_data_fields = [
        ("title", ""),
        ("data", ""),
        ("service", "")
    ]

    service = forms.ModelChoiceField(queryset=UserService.objects.filter(service__status=True),
                                     required=True)

    def save_plugin_data(self, request=None):
        service = self.cleaned_data.get('service', None)

        if service:
            service_name = service.service.name.lower()
            form = ServiceFormFactory.factory(service_name)(request.POST)

            if form.is_valid():
                form_data = form.cleaned_data
                self.cleaned_data['service'] = service.pk
                self.cleaned_data['title'] = service.service.name
                self.cleaned_data['data'] = form_data
            else:
                raise ValueError(form.errors)
