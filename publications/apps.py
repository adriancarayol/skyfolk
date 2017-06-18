from django.apps import AppConfig


class PublicationAppConfig(AppConfig):
    name = 'publications'

    def ready(self):
        from publications import signals
