from django.apps import AppConfig


class PublicationGroupGalleryAppConfig(AppConfig):
    name = "publications_gallery_groups"

    def ready(self):
        super(PublicationGroupGalleryAppConfig, self).ready()
        from publications_gallery_groups import signals
