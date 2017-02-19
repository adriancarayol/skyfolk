from django.dispatch import receiver
from django.db.models.signals import post_save
from .tasks import send_to_stream, send_to_profile
from .models import Publication

@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    """
    Enviamos notificacion a los que visitan nuestro perfil
    """
    if not created: # Cuando llamamos a .save() enviamos notificacion
        if not instance.parent:
            send_to_profile.delay(instance.id, None)
        else:
            send_to_profile.delay(instance.id, "reply")

        # Enviamos al tablon de noticias (inicio)
        if (instance.author == instance.board_owner):
            send_to_stream.delay(instance.author.id, instance.id)

