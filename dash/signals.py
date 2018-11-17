import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from dash.models import DashboardEntry


@receiver(post_save, sender=DashboardEntry)
def handle_new_dashboard_entry(sender, instance, created, **kwargs):
    service_name = instance.plugin_uid.split('_')[0]
    if service_name.lower() == 'service':
        try:
            response = requests.post('http://go_skyfolk:1800/update/', data={'id': instance.pk})
            print(response)
        except requests.RequestException:
            pass
