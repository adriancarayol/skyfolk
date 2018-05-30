import os
import uuid

import requests
from io import BytesIO
from django.conf import settings
from urllib.parse import urlparse
from django.core.files.base import ContentFile


def split_url(url):
    parse_object = urlparse(url)
    return parse_object.netloc, parse_object.path


def get_url_tail(url):
    return url.split('/')[-1]


def get_extension(filename):
    return os.path.splitext(filename)[1]


def pil_to_django(image, format="JPEG"):
    fobject = BytesIO()
    image.save(fobject, format=format)
    return ContentFile(fobject.getvalue())


def retrieve_image(url):
    response = requests.get(url)
    return BytesIO(response.content)


def generate_path_video(ext='mp4'):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    filename = "%s.%s" % (uuid.uuid4(), ext)
    path = os.path.join(settings.MEDIA_ROOT, 'photologue/videos')
    return [os.path.join(path, filename),
            os.path.join('photologue/videos', filename)]


def generate_thumbnail_path_video(ext='jpg'):
    filename = "%s.%s" % (uuid.uuid4(), ext)
    path = os.path.join(settings.MEDIA_ROOT, 'videos/thumbnails')
    return [os.path.join(path, filename),
            os.path.join('photologue/videos/thumbnails', filename)]
