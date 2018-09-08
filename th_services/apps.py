from django.apps import AppConfig


class ThServicesConfiguration(AppConfig):
    name = 'th_services'

    def ready(self):
        super(ThServicesConfiguration, self).ready()
