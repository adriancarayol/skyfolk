from django.apps import AppConfig


class ThTumblrAppConfiguration(AppConfig):
    name = 'th_services.th_tumblr'

    def ready(self):
        super(ThTumblrAppConfiguration, self).ready()
