from django.contrib import admin
from external_services.models import Services, UserService


admin.site.register(Services)
admin.site.register(UserService)
