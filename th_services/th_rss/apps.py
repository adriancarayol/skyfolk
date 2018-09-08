from django.apps import AppConfig


class ThRssAppConfiguration(AppConfig):
    name = 'th_services.th_rss'

    def ready(self):
        super(ThRssAppConfiguration, self).ready()
