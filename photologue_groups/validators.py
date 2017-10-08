import os
import mimetypes
import requests
import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
]

VALID_IMAGE_MIMETYPES = [
    "image"
]


def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    return any([url.endswith(e) for e in extension_list])


def valid_url_mimetype(url, mimetype_list=VALID_IMAGE_MIMETYPES):
    mimetype, encoding = mimetypes.guess_type(url)
    if mimetype:
        return any([mimetype.startswith(m) for m in mimetype_list])
    else:
        return False


def get_mimetype(fobject):
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(fobject.read(1024))
    fobject.seek(0)
    return mimetype


def valid_image_mimetype(fobject):
    mimetype = get_mimetype(fobject)
    if mimetype:
        return mimetype.startswith('image')
    else:
        return False

def valid_image_size(image, max_size=settings.BACK_IMAGE_DEFAULT_SIZE):
    width, height = image.size
    if (width * height) > max_size:
        return (False, "La imagen es muy larga.")
    return (True, image)

def image_exists(url):
    try:
        r = requests.head(url)
    except:
        return False

    try:
        length = int(r.headers['Content-length'])
    except:
        length = 0

    if length > settings.BACK_IMAGE_DEFAULT_SIZE:
        return False

    return r.status_code == requests.codes.ok


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.gif', '.png', '.jpeg', '.jpg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Tipo de fichero no soportado.')


def validate_extension(ext):
    valid_extensions = ['.gif', '.png', '.jpeg', '.jpg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Tipo de fichero no soportado.')


def validate_video(value):
    ''' if value.file is an instance of InMemoryUploadedFile, it means that the
    file was just uploaded with this request (i.e., it's a creation process,
    not an editing process. '''
    if isinstance(value, InMemoryUploadedFile) and value.file.content_type.split('/').lower()[
        1] not in settings.VIDEO_EXTENTIONS:
        raise ValidationError('Por favor, suba un archivo de vídeo.')
