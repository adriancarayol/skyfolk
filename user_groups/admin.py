# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import UserGroups, GroupTheme


class GroupAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name')
    list_filter = ('owner', )

class ThemeGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'description', 'image')
    list_filter = ('board_group', 'owner')

admin.site.register(UserGroups, GroupAdmin)
admin.site.register(GroupTheme, ThemeGroupAdmin)
