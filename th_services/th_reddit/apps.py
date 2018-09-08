from django.apps import AppConfig


class ThRedditAppConfiguration(AppConfig):
    name = 'th_services.th_reddit'

    def ready(self):
        super(ThRedditAppConfiguration, self).ready()
