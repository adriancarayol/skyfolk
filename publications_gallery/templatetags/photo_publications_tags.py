from publications_gallery.models import PublicationPhoto
from django import template

register = template.Library()

# Para publicaciones en imagenes

# Devuelve el numero total de veces que se ha compartido un comentario
@register.filter(name='user_in_liked_photo_list')
def user_in_liked_photo_list(pub, user_pk):
    if PublicationPhoto.objects.filter(id=pub, user_give_me_like__id=user_pk).exists():
        return True
    return False


# Devuelve el numero total de me gustas
@register.filter(name='user_in_hated_photo_list')
def user_in_hated_photo_list(pub, user_pk):
    if PublicationPhoto.objects.filter(id=pub, user_give_me_hate__id=user_pk).exists():
        return True
    return False


# Devuelve el numero total de no me gusta

@register.filter(name='user_in_shared_list')
def user_in_shared_list(pub, user_pk):
    return False