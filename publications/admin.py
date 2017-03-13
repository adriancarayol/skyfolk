# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Publication


class PublicationBaseAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created', )
    list_filter = ('created', 'author', )


admin.site.register(Publication, PublicationBaseAdmin)
