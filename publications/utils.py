from avatar.models import Avatar
from user_profile.models import UserProfile
import re
import bleach
from django.conf import settings

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)

def get_author_avatar(authorpk):
    """
    Devuelve el avatar del autor de la publicacion pasada como parametro
    """
    try:
        avatars = Avatar.objects.get(user=authorpk, primary=True)
    except Avatar.DoesNotExist:
        avatars = None

    if avatars:
        return avatars.get_absolute_url()
    else:
        return UserProfile.objects.get(user=authorpk).gravatar


def parse_string(content):
    """
    Busca hashtags, menciones y comprueba que el formato
    de un string es correcto (se acepta como contenido en la web)
    """

    # FIND HASHTAGS
    hashtags = [tag.strip() for tag in content.split() if tag.startswith("#")]
    hashtags = set(hashtags)
    for tag in hashtags:
        if tag.endswith((',', '.')):
            tag = tag[:-1]
        content = content.replace(tag,
                                            '<a href="/search/">{0}</a>'.format(tag))

    # CLEAN CONTENT
    content = content.replace('\n', '').replace('\r', '')
    content = bleach.clean(content, tags=ALLOWED_TAGS,
                                attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
    bold = re.findall('\*[^\*]+\*', content)
    ''' Bold para comentario '''
    for b in bold:
        content = content.replace(b, '<b>%s</b>' % (b[1:len(b) - 1]))
    ''' Italic para comentario '''
    italic = re.findall('~[^~]+~', content)
    for i in italic:
        content = content.replace(i, '<i>%s</i>' % (i[1:len(i) - 1]))
    ''' Tachado para comentario '''
    tachado = re.findall('\^[^\^]+\^', content)
    for i in tachado:
        content = content.replace(i, '<strike>%s</strike>' % (i[1:len(i) - 1]))

    return content