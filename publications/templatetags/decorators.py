from bs4 import BeautifulSoup
from django import template

from publications.models import Publication

register = template.Library()


# Devuelve el numero total de veces que se ha compartido un comentario
@register.filter(name="user_in_liked_list")
def user_in_liked_list(pub, user_pk):
    return Publication.objects.filter(
        id=pub, user_give_me_like__id=user_pk, deleted=False
    ).exists()


# Devuelve el numero total de me gustas
@register.filter(name="user_in_hated_list")
def user_in_hated_list(pub, user_pk):
    return Publication.objects.filter(
        id=pub, user_give_me_hate__id=user_pk, deleted=False
    ).exists()


# Devuelve el numero total de no me gusta
@register.filter(name="user_in_shared_list")
def user_in_shared_list(pub, user_pk):
    return Publication.objects.filter(
        shared_publication_id=pub, author_id=user_pk, deleted=False
    ).exists()


# Returns inner text between html tags
@register.filter(name="inner_text_between_html_tags")
def inner_text_between_html_tags(content):
    soup = BeautifulSoup(content)
    text = soup.get_text()
    return text
