from django.apps import AppConfig


class PublicationAppConfig(AppConfig):
    name = 'publications'

    def ready(self):
        super(PublicationAppConfig, self).ready()
