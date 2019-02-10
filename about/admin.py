from django.contrib import admin
from about.forms import PostAdminForm
from about.models import PublicationBlog


class AuthorAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('author', 'created', 'content', )


admin.site.register(PublicationBlog, AuthorAdmin)
