from django.apps import AppConfig


class ExternalServicesConfiguration(AppConfig):
    name = 'external_services'

    def ready(self):
        super(ExternalServicesConfiguration, self).ready()
