from django.db import models
from photologue.models import Gallery, Photo
from taggit.managers import TaggableManager
from django.contrib.auth.models import User


class GalleryExtended(models.Model):
    """
    Galeria de fotos para un usuario
    """
    # Link back to Photologue's Gallery model.
    gallery = models.OneToOneField(Gallery, related_name='gallery_extended')

    # This is the important bit - where we add in the tags.
    tags = TaggableManager(blank=True)

    owner = models.ForeignKey(User, null=True, blank=True, related_name='user_gallery')

    class Meta:
        verbose_name = u'Extra fields'

    def __str__(self):
        return self.gallery.title

class PhotoExtended(models.Model):
    """
    Imagenes de un usuario
    """

    photo = models.OneToOneField(Photo, related_name='photo_extended')

    tags = TaggableManager(blank=True)

    owner = models.ForeignKey(User, null=True, blank=True, related_name='user_photos')

    class Meta:
        verbose_name = u'Extra fields'

    def __str__(self):
        return self.photo.title