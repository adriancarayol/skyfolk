import uuid, os, hashlib
from django.conf import settings
from django.core.cache import cache
from django.utils import six
from django.template.defaultfilters import slugify

try:
    from django.utils.encoding import force_bytes
except ImportError:
    force_bytes = str

cached_funcs = set()

def handle_uploaded_file(f, file_id):
    filename, file_extension = os.path.splitext(f.name)
    dir_path = settings.MEDIA_ROOT + '/back_images/'

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = dir_path + file_id + file_extension

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_cache_key(user_or_username, size, prefix):
    if isinstance(user_or_username, 'user_profile.models.NodeProfile'):
        user_or_username = user_or_username.title

    key = six.u('%s_%s_%s') % (prefix, user_or_username, size)
    return six.u('%s_%s') % (slugify(key)[:100],
                             hashlib.md5(force_bytes(key)).hexdigest())

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