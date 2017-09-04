from django.apps import AppConfig


class PublicationGroupAppConfig(AppConfig):
    name = 'publications_groups'

    def ready(self):
        super(PublicationGroupAppConfig, self).ready()
        from publications_groups import signals