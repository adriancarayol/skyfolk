from django.db.models.signals import post_save
from django.dispatch import receiver
from dash.models import DashboardEntry
from external_services.tasks import update_external_services


@receiver(post_save, sender=DashboardEntry)
def handle_new_dashboard_entry(sender, instance, created, **kwargs):
    service_name = instance.plugin_uid.split("_")
    service_name = "".join(service_name[:-1])

    if service_name.lower() == "service":
        update_external_services.delay(instance.pk)
