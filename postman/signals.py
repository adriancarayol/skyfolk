from django.db.models.signals import post_save
from .models import Message
from django.dispatch import receiver
from notifications.signals import notify


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    if created:
        notify.send(instance.sender, actor=instance.sender.username,
                    recipient=instance.recipient,
                    verb=u'¡tienes un nuevo mensaje privado!',
                    description='<a href="%s">Ver</a>' % ('/messages/view/' + str(instance.id)),
                    level='message')
