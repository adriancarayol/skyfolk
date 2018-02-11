from django.apps import AppConfig


class ThRedditAppConfiguration(AppConfig):
    name = 'th_reddit'

    def ready(self):
        super(ThRedditAppConfiguration, self).ready()
