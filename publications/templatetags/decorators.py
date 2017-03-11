import re

from django import template

from publications.models import Publication

register = template.Library()


# Remplaza ocurrencias en el contenido del comentario
@register.filter(name='replace_decorators')
def replace_tags(value):
    bold = re.findall('\*[^\*]+\*', value)
    ''' Bold para comentario '''
    for b in bold:
        value = value.replace(b, '<b>%s</b>' % (b[1:len(b) - 1]))
    ''' Italic para comentario '''
    italic = re.findall('~[^~]+~', value)
    for i in italic:
        value = value.replace(i, '<i>%s</i>' % (i[1:len(i) - 1]))
    ''' Tachado para comentario '''
    tachado = re.findall('\^[^\^]+\^', value)
    for i in tachado:
        value = value.replace(i, '<strike>%s</strike>' % (i[1:len(i) - 1]))
    return value


# Devuelve el numero total de veces que se ha compartido un comentario
@register.filter(name='total_shares')
def total_shares(pub):
    total = Publication.objects.get(pk=pub).user_share_me.count()
    if total > 0:
        return total
    else:
        return ""


# Devuelve el numero total de me gustas
@register.filter(name='total_likes')
def total_likes(pub):
    total = Publication.objects.get(pk=pub).user_give_me_like.count()
    if total > 0:
        return total
    else:
        return ""


# Devuelve el numero total de no me gusta
@register.filter(name='total_hates')
def total_hates(pub):
    total = Publication.objects.get(pk=pub).user_give_me_hate.count()
    return total
