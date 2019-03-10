from django.contrib import admin
from awards.models import UserRank


class UserRankAdmin(admin.ModelAdmin):
    list_display = ('name', 'reached_with')


admin.site.register(UserRank, UserRankAdmin)
