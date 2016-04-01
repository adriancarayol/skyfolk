from django import template
import re
register = template.Library()


@register.filter(name='replace_tags_mentions')
def replace_tags(value):
    bold = re.findall('\*[^\*]+\*', value)
    ''' Bold para comentario '''
    for b in bold:
        value = value.replace(b, '<b>%s</b>' % (b[1:len(b)-1]))
    ''' Italic para comentario '''
    italic = re.findall('_[^_]+_', value)
    for i in italic:
        value = value.replace(i, '<i>%s</i>' % (i[1:len(i) - 1]))
    ''' Tachado para comentario '''
    tachado = re.findall('~[^~]+~', value)
    for i in tachado:
        value = value.replace(i, '<strike>%s</strike>' % (i[1:len(i) - 1]))
    return value