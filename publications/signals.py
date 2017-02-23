from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Publication
from django.core.exceptions import ValidationError

@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    """
    Enviamos notificacion a los que visitan nuestro perfil
    """
    if created:
        try:
            instance.add_hashtag()
            instance.add_mentions()
            instance.parse_content()
        except Exception:
            instance.delete()
            raise ValidationError("No se permite ese contenido.")