from django.apps import AppConfig


class ThEvernoteAppConfiguration(AppConfig):
    name = 'th_evernote'

    def ready(self):
        super(ThEvernoteAppConfiguration, self).ready()
