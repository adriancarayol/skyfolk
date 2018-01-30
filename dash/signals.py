import json
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .contrib.plugins.poll.models import Poll
from dash_services.models import TriggerService
from .models import DashboardEntry
from io import StringIO


@receiver(post_delete, sender=DashboardEntry)
def handle_delete_entry(sender, instance, *args, **kwargs):
    data = instance.plugin_data
    io = StringIO(data)
    parse_data = json.load(io)
    trigger_id = parse_data.get('trigger', None)

    if trigger_id is not None:
        TriggerService.objects.filter(id=trigger_id).delete()


@receiver(post_save, sender=DashboardEntry)
def handle_new_entry(sender, instance, created, **kwargs):
    if instance.plugin_uid.split('_')[0] == 'poll':
        data = instance.plugin_data
        io = StringIO(data)
        parse_data = json.load(io)
        title = parse_data.get('title', None)
        description = parse_data.get('description', None)

        if created:
            poll = Poll.objects.create()

        if poll:
            poll_id = poll.id
        else:
            poll_id = parse_data.get('poll', None)

        data = {
            'poll': poll_id,
            'title': title,
            'description': description
        }

        obj = json.dumps(data)

        instance.plugin_data = obj