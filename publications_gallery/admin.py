# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import PublicationPhoto, ExtraContentPubPhoto, PublicationPhotoVideo, \
        PublicationPhotoImage


class PublicationBaseAdmin(admin.ModelAdmin):
    list_display = ('p_author', 'content', 'created', 'board_photo')
    list_filter = ('created', 'p_author', 'parent', 'board_photo')


class ExtraContentAdmin(admin.ModelAdmin):
    list_display = ('publication', 'url', 'title')
    list_filter = ('publication', )


class PublicationVideoAdmin(admin.ModelAdmin):
    list_display = ('publication', )
    list_filter = ('publication', )


class PublicationImageAdmin(admin.ModelAdmin):
    list_display = ('publication', )
    list_filter = ('publication', )


admin.site.register(ExtraContentPubPhoto, ExtraContentAdmin)
admin.site.register(PublicationPhotoVideo, PublicationVideoAdmin)
admin.site.register(PublicationPhotoImage, PublicationImageAdmin)
admin.site.register(PublicationPhoto, PublicationBaseAdmin)
