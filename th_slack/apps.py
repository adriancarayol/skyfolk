from django.apps import AppConfig


class ThSlackAppConfiguration(AppConfig):
    name = 'th_slack'

    def ready(self):
        super(ThSlackAppConfiguration, self).ready()
