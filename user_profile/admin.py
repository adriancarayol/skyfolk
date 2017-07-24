# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Request, AuthDevices


class RequestFriendAdmin(admin.ModelAdmin):
    list_display = ('emitter', 'status', 'receiver', 'created', )
    list_filter = ('emitter', 'status', 'receiver', 'created', )


class AuthDevicesAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'browser_token', )
    list_filter = ('user_profile', )


admin.site.register(Request, RequestFriendAdmin)
admin.site.register(AuthDevices, AuthDevicesAdmin)
