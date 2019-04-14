import hashlib
import json
import os

from PIL import Image
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.defaultfilters import slugify
from django.utils import six

try:
    from django.utils.encoding import force_bytes
except ImportError:
    force_bytes = str

cached_funcs = set()


def handle_uploaded_file(f, file_id):
    filename, file_extension = os.path.splitext(f.name)
    dir_path = settings.MEDIA_ROOT + "/back_images/"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = dir_path + file_id + file_extension

    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_cache_key(user_or_username, size, prefix):
    key = six.u("%s_%s_%s") % (prefix, user_or_username, size)
    return six.u("%s_%s") % (
        slugify(key)[:100],
        hashlib.md5(force_bytes(key)).hexdigest(),
    )


def cache_set(key, value):
    cache.set(key, value, settings.BACK_IMAGE_CACHE_TIMEOUT)
    return value


def cache_result(default_size=settings.BACK_IMAGE_DEFAULT_SIZE):
    def decorator(func):
        def cached_func(user, size=None, **kwargs):
            prefix = func.__name__
            cached_funcs.add(prefix)
            key = get_cache_key(user, size or default_size, prefix=prefix)
            result = cache.get(key)
            if result is None:
                result = func(user, size or default_size, **kwargs)
                cache_set(key, result)
            return result

        return cached_func

    return decorator


def invalidate_cache(user, size=None):
    """
    Function to be called when saving or changing an user's avatars.
    """
    sizes = set(120)
    if size is not None:
        sizes.add(size)
    for prefix in cached_funcs:
        for size in sizes:
            cache.delete(get_cache_key(user, size, prefix))


def group_name(id):
    """
    Devuelve el nombre del canal para enviar las notificaciones
    """
    return "users-%s" % id


def notification_channel(id):
    """
    Devuelve el nombre del canal notification para cada usuario
    """
    return "notification-%s" % id


def news_channel(id):
    """
    Devuelve el nombre del canal para enviar actualizaciones
    al tablon de inicio
    """
    return "news-%s" % id


def crop_image(image, filename, request):
    """
    Recortar imagen
    """
    img_data = dict(request.POST.items())
    x = None  # Coordinate x
    y = None  # Coordinate y
    w = None  # Width
    h = None  # Height
    rotate = None  # Rotate
    is_cutted = True
    for key, value in img_data.items():  # Recorremos las opciones de recorte
        if (
            key == "avatar_cut" and value == "false"
        ):  # Comprobamos si el usuario ha recortado la foto
            is_cutted = False
            break
        if key == "avatar_data":
            str_value = json.loads(value)
            x = str_value.get("x")
            y = str_value.get("y")
            w = str_value.get("width")
            h = str_value.get("height")
            rotate = str_value.get("rotate")

    if image.size > settings.BACK_IMAGE_DEFAULT_SIZE:
        raise ValueError("Backimage > 5MB!")

    im = Image.open(image)
    fill_color = (255, 255, 255, 0)
    if im.mode in ("RGBA", "LA"):
        background = Image.new(im.mode[:-1], im.size, fill_color)
        background.paste(im, im.split()[-1])
        im = background
    if is_cutted:  # el usuario ha recortado la foto
        tempfile = im.rotate(-rotate, expand=True)
        tempfile = tempfile.crop((int(x), int(y), int(w + x), int(h + y)))
        tempfile_io = six.BytesIO()
        tempfile.save(tempfile_io, format="JPEG", optimize=True, quality=90)
        tempfile_io.seek(0)
        image_file = InMemoryUploadedFile(
            tempfile_io, None, filename, "image/jpeg", tempfile_io.tell(), None
        )
    else:  # no la recorta, optimizamos la imagen
        im.thumbnail((1500, 630), Image.ANTIALIAS)
        tempfile_io = six.BytesIO()
        im.save(tempfile_io, format="JPEG", optimize=True, quality=90)
        tempfile_io.seek(0)
        image_file = InMemoryUploadedFile(
            tempfile_io, None, filename, "image/jpeg", tempfile_io.tell(), None
        )

    return image_file


def make_pagination_html(current_page, total_pages, full_path=""):
    pagination_string = ""

    if current_page > 1:
        pagination_string += (
            '<li><a href="%s?page=%s"><i class="material-icons">chevron_left</i></a></li>'
            % (full_path, current_page - 1)
        )

    pagination_string += (
        '<li class="active blue darken-1 white-text"><span> %d </span></li>'
        % current_page
    )
    count_limit = 1
    value = current_page - 1

    while value > 0 and count_limit < 5:
        pagination_string = (
            '<li class="waves-effect"><a href="%s?page=%s">%s</a></li>'
            % (full_path, value, value)
            + pagination_string
        )
        value -= 1
        count_limit += 1

    value = current_page + 1

    while value < total_pages and count_limit < 10:
        pagination_string = (
            pagination_string
            + "<li><a href='%s?page=%s'>%s</a></li>" % (full_path, value, value)
        )
        value += 1
        count_limit += 1

    if current_page < total_pages:
        pagination_string += (
            '<li><a href="%s?page=%s"><i class="material-icons">chevron_right</i></a></li>'
            % (full_path, current_page + 1)
        )

    pagination_string = '<ul class="center pagination">' + pagination_string + "</ul>"
    return pagination_string
