from django.apps import AppConfig


class PublicationThemeAppConfig(AppConfig):
    name = 'publications_groups.themes'

    def ready(self):
        super(PublicationThemeAppConfig, self).ready()
        from publications_groups.themes import signals