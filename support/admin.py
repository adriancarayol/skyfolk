from django.contrib import admin
from .models import SupportPasswordModel


class SupportPasswordAdmin(admin.ModelAdmin):
    list_display = ("user", "title")
    list_filter = ("user",)


admin.site.register(SupportPasswordModel, SupportPasswordAdmin)
