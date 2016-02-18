from django import template
import re
register = template.Library()


@register.filter(name='replace_tags_mentions')
def replace_tags(value):
    hashtags = re.findall('#[a-zA-Z][a-zA-Z0-9_]*', value)
    ''' Tags para comentario '''
    for hashtag in hashtags:
        value =value.replace(hashtag, '<a href="/search/">%s</a>' % (hashtag))
    ''' Menciones para comentario '''
    menciones = re.findall('\\@[a-zA-Z0-9_]+', value)
    for mencion in menciones:
        value = value.replace(mencion, '<a href="/profile/%s">%s</a>' % (mencion[1:], mencion))
    return value
