import os
import requests
from io import BytesIO

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
