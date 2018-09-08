from django.contrib import admin

from .models import PublicationBlog


class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(PublicationBlog, AuthorAdmin)