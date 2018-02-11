from django.apps import AppConfig


class ThPelicanAppConfiguration(AppConfig):
    name = 'th_pelican'

    def ready(self):
        super(ThPelicanAppConfiguration, self).ready()
