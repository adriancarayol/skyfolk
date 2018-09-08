from django.db.models.signals import post_save
from django.dispatch import receiver
from badgify.models import Award, Badge
from notifications.signals import notify
from .models import Message


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    messages_count = Message.objects.filter(sender=instance.sender).count()

    if messages_count:
        Award.objects.get_or_create(user=instance.sender, badge=Badge.objects.get(slug='first-direct-message'))
        
    if created:
        notify.send(instance.sender, actor=instance.sender.username,
                    recipient=instance.recipient,
                    verb=u'¡tienes un nuevo mensaje privado!',
                    description='Has recibido un nuevo mensaje privado de: @{0} <a href="{1}">Ver</a>.'.format(
                        instance.sender.username, '/messages/view/' + str(instance.id)),
                    level='message')
