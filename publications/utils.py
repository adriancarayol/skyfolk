import os
import subprocess
import uuid

import bleach
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.uploadedfile import InMemoryUploadedFile

from avatar.models import Avatar
from user_profile.models import Profile

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)


def get_channel_name(id):
    """
    Devuelve el channel para una publicacion
    """
    return "publication-%s" % id


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
        return Profile.objects.get(user_id=authorpk).gravatar


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


def validate_video(value):
    ''' if value.file is an instance of InMemoryUploadedFile, it means that the
    file was just uploaded with this request (i.e., it's a creation process,
    not an editing process. '''
    if isinstance(value.video, InMemoryUploadedFile) and value.file.content_type.split('/').lower()[
        1] not in settings.VIDEO_EXTENTIONS:
        raise ValueError('Please upload a valid video file')


def recursive_node_to_dict(node):
    """
        Obtiene los descendientes de nivel 1
        de una publicacion
    """
    result = {
        'id': node.pk,
        'content': node.content,
        'created': naturaltime(node.created),
        'author__username': node.author.username
    }
    children = [recursive_node_to_dict(c) for c in node.get_descendants().filter(deleted=False, level__lte=1)[:10]]
    if children:
        result['children'] = children
    return result
