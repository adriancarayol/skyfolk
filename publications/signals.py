from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .tasks import send_to_stream
from .models import Publication


@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    """
    Enviamos notificacion a los que visitan nuestro perfil
    """
    if created:
        instance.add_hashtag()


@receiver(pre_save, sender=Publication, dispatch_uid='publication_pre_save')
def publication_pre_handler(sender, instance, **kwargs):
    if not instance.parent:
        instance.send_notification()
    else:
        instance.send_notification(type="reply")

    # Enviamos al tablon de noticias (inicio)
    if instance.author == instance.board_owner:
        send_to_stream.delay(instance.author.id, instance.id)