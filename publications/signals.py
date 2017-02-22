from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Publication


@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    """
    Enviamos notificacion a los que visitan nuestro perfil
    """
    if created:
        instance.add_hashtag()