from django.contrib import admin
from .models import GalleryExtended, PhotoExtended
from photologue.models import Gallery
from photologue.models import Photo
from photologue.admin import GalleryAdmin as GalleryAdminDefault
from photologue.admin import PhotoAdmin as PhotoAdminDefault

class GalleryExtendedInline(admin.StackedInline):
    model = GalleryExtended

class PhotoExtendedInline(admin.StackedInline):
    model = PhotoExtended


class GalleryAdmin(GalleryAdminDefault):
    inlines = [GalleryExtendedInline, ]

class PhotoAdmin(PhotoAdminDefault):
    inlines = [PhotoExtendedInline, ]


admin.site.unregister(Gallery)
admin.site.unregister(Photo)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Photo, PhotoAdmin)