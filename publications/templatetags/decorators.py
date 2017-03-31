import re

from django import template

from publications.models import Publication, SharedPublication

register = template.Library()

# Devuelve el numero total de veces que se ha compartido un comentario
@register.filter(name='user_in_liked_list')
def user_in_liked_list(pub, user_pk):
    if Publication.objects.filter(id=pub, user_give_me_like__id=user_pk).exists():
        return True
    return False


# Devuelve el numero total de me gustas
@register.filter(name='user_in_hated_list')
def user_in_hated_list(pub, user_pk):
    if Publication.objects.filter(id=pub, user_give_me_hate__id=user_pk).exists():
        return True
    return False


# Devuelve el numero total de no me gusta
@register.filter(name='user_in_shared_list')
def user_in_shared_list(pub, user_pk):
    if SharedPublication.objects.filter(publication_id=pub, by_user=user_pk).exists():
        return True
    return False
