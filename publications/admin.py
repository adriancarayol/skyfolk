# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Publication, ExtraContent, PublicationVideo, \
        PublicationImage, PublicationDeleted


class PublicationBaseAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created', 'board_owner')
    list_filter = ('created', 'author', 'parent', 'board_owner')


class ExtraContentAdmin(admin.ModelAdmin):
    list_display = ('publication', 'url', 'title')
    list_filter = ('publication', )


class PublicationVideoAdmin(admin.ModelAdmin):
    list_display = ('publication', )
    list_filter = ('publication', )


class PublicationImageAdmin(admin.ModelAdmin):
    list_display = ('publication', )
    list_filter = ('publication', )


class PublicationDeletedAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created')
    list_filter = ('author', 'created', 'type_publication')


admin.site.register(ExtraContent, ExtraContentAdmin)
admin.site.register(PublicationVideo, PublicationVideoAdmin)
admin.site.register(PublicationImage, PublicationImageAdmin)
admin.site.register(PublicationDeleted, PublicationDeletedAdmin)
admin.site.register(Publication, PublicationBaseAdmin)
