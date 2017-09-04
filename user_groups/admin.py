# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import UserGroups


class GroupAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name')
    list_filter = ('owner', )

admin.site.register(UserGroups, GroupAdmin)
