from django.apps import AppConfig


class ThTwitterAppConfiguration(AppConfig):
    name = 'th_twitter'

    def ready(self):
        super(ThTwitterAppConfiguration, self).ready()
