from django.conf import settings
from PIL import Image

from appconf import AppConf


class AvatarConf(AppConf):
    DEFAULT_SIZE = 120
    RESIZE_METHOD = Image.ANTIALIAS
    STORAGE_DIR = 'avatars'
    PATH_HANDLER = 'avatar.models.avatar_path_handler'
    GRAVATAR_BASE_URL = 'https://www.gravatar.com/avatar/'
    GRAVATAR_FIELD = 'email'
    GRAVATAR_BACKUP = True
    GRAVATAR_DEFAULT = 'http://pre.skyfolk.net/static/img/nuevo.png'
    AVATAR_GRAVATAR_FORCEDEFAULT = False
    DEFAULT_URL = '/img/nuevo.png'
    MAX_AVATARS_PER_USER = 5
    MAX_SIZE = 1024 * 1024
    THUMB_FORMAT = 'GIF' # Cambiar a jpeg si no se desean movimientos.
    THUMB_QUALITY = 85
    HASH_FILENAMES = True
    HASH_USERDIRNAMES = False
    EXPOSE_USERNAMES = True
    ALLOWED_FILE_EXTS = None
    CACHE_TIMEOUT = 60 * 60
    STORAGE = settings.DEFAULT_FILE_STORAGE
    CLEANUP_DELETED = True
    AUTO_GENERATE_SIZES = (DEFAULT_SIZE,)
    FACEBOOK_BACKUP = False
    FACEBOOK_GET_ID = None
    CACHE_ENABLED = True
    RANDOMIZE_HASHES = True

    def configure_auto_generate_avatar_sizes(self, value):
        return value or getattr(settings, 'AVATAR_AUTO_GENERATE_SIZES',
                                (self.DEFAULT_SIZE,))
