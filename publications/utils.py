import re
import uuid
import bleach
import os
import subprocess
from avatar.models import Avatar
from user_profile.models import NodeProfile
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
        return NodeProfile.nodes.get(user_id=authorpk).gravatar


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
    """
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
    """
    return content


def remove_duplicates_in_list(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def generate_path_video(ext='mp4'):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return [os.path.join('skyfolk/media/publications/videos', filename), os.path.join('publications/videos', filename)]


def convert_avi_to_mp4(avi_file_path, output_name):
    process = subprocess.call("ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}'".format(input = avi_file_path, output = output_name), shell=True)