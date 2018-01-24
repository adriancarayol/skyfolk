from django.apps import AppConfig


class ThPocketAppConfiguration(AppConfig):
    name = 'th_pocket'

    def ready(self):
        super(ThPocketAppConfiguration, self).ready()
