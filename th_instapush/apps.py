from django.apps import AppConfig


class ThInstaPushAppConfiguration(AppConfig):
    name = 'th_instapush'

    def ready(self):
        super(ThInstaPushAppConfiguration, self).ready()
