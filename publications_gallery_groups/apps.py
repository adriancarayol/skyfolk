from django.apps import AppConfig


class PublicationGalleryAppConfig(AppConfig):
    name = 'publications_gallery'

    def ready(self):
        super(PublicationGalleryAppConfig, self).ready()
        from publications_gallery import signals
