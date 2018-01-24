import json
from django.db.models.signals import post_delete
from django.dispatch import receiver

from dash_services.models import TriggerService
from .models import DashboardEntry
from io import StringIO


@receiver(post_delete, sender=DashboardEntry)
def handle_delete_entry(sender, instance, *args, **kwargs):
    data = instance.plugin_data
    io = StringIO(data)
    parse_data = json.load(io)
    print(parse_data)
    trigger_id = parse_data.get('trigger', None)

    if trigger_id is not None:
        TriggerService.objects.filter(id=trigger_id).delete()
