from django.apps import AppConfig


class ThWallabagAppConfiguration(AppConfig):
    name = 'th_wallabag'

    def ready(self):
        super(ThWallabagAppConfiguration, self).ready()
