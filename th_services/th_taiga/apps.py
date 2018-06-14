from django.apps import AppConfig


class ThTaigaAppConfiguration(AppConfig):
    name = 'th_services.th_taiga'

    def ready(self):
        super(ThTaigaAppConfiguration, self).ready()
