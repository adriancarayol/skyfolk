import json
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from external_services.models import UserService
from dash.models import DashboardEntry


@receiver(pre_delete, sender=UserService)
def pre_delete_user_service(sender, instance, *args, **kwargs):
    user_service_id = instance.id
    user = instance.user
    user_services = DashboardEntry.objects.filter(user=user)

    for user_service in user_services:
        data = json.loads(user_service.plugin_data)

        if "service" not in data:
            continue

        if data["service"] == user_service_id:
            user_service.delete()
