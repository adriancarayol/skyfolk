from django import template

from publications.models import Publication
from publications_gallery.models import PublicationPhoto

register = template.Library()

# Para publicaciones en imagenes

# Devuelve el numero total de veces que se ha compartido un comentario
@register.filter(name='user_in_liked_photo_list')
def user_in_liked_photo_list(pub, user_pk):
    return PublicationPhoto.objects.filter(id=pub, user_give_me_like__id=user_pk).exists()


# Devuelve el numero total de me gustas
@register.filter(name='user_in_hated_photo_list')
def user_in_hated_photo_list(pub, user_pk):
    return PublicationPhoto.objects.filter(id=pub, user_give_me_hate__id=user_pk).exists()


@register.filter(name='user_in_shared_photo_list')
def user_in_shared_photo_list(pub, user_pk):
    return Publication.objects.filter(shared_photo_publication_id=pub, author_id=user_pk, deleted=False).exists()