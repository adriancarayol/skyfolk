from django.apps import AppConfig


class ThTwitterAppConfiguration(AppConfig):
    name = 'th_services.th_twitter'

    def ready(self):
        super(ThTwitterAppConfiguration, self).ready()
