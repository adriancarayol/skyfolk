from django import template
import re
register = template.Library()


@register.filter(name='replace_tags_mentions')
def replace_tags(value):
    bold = re.findall('\*[^\*]+\*', value)
    ''' Bold para comentario '''
    for b in bold:
        value = value.replace(b, '<b>%s</b>' % (b[1:len(b)-1]))
    italic = re.findall('_[^_]+_', value)
    for i in italic:
        value = value.replace(i, '<i>%s</i>' % (i[1:len(i) - 1]))
    ''' Tags para comentario '''
    hashtags = re.findall('#[a-zA-Z][a-zA-Z0-9_]*', value)
    for hashtag in hashtags:
        value = value.replace(hashtag, '<a href="/search/">%s</a>' % (hashtag))
    ''' Menciones para comentario '''
    menciones = re.findall('\\@[a-zA-Z0-9_]+', value)
    for mencion in menciones:
        value = value.replace(mencion, '<a href="/profile/%s">%s</a>' % (mencion[1:], mencion))
    return value