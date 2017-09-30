import logging
import mimetypes
import os
import tempfile
import unicodedata
import uuid
from datetime import datetime
from importlib import import_module
from inspect import isclass
from io import BytesIO
from os.path import splitext
from urllib.parse import urlparse

import exifread
import magic
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import force_text, smart_str, filepath_to_uri
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from uuslug import uuslug
from photologue.models import ImageModel
from photologue.utils.utils import split_url, get_url_tail, retrieve_image, pil_to_django
from user_groups.models import UserGroups
from .tasks import generate_thumbnails, generate_video_thumbnail
from .validators import validate_file_extension, validate_video, validate_extension, image_exists, valid_image_mimetype, \
    valid_image_size

# Required PIL classes may or may not be available from the root namespace
# depending on the installation method used.
try:
    import Image
    import ImageFile
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageFile
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError(
            'Photologue was unable to import the Python Imaging Library. Please confirm it`s installed and available '
            'on your current Python path.')

from .utils.reflection import add_reflection
from .utils.watermark import apply_watermark
from .managers import PhotoQuerySet

logger = logging.getLogger('photologue.models')

# Default limit for publications_gallery.latest
LATEST_LIMIT = getattr(settings, 'PHOTOLOGUE_GALLERY_LATEST_LIMIT', None)

# Number of random images from the publications_gallery to display.
SAMPLE_SIZE = getattr(settings, 'PHOTOLOGUE_GALLERY_SAMPLE_SIZE', 5)

# max_length setting for the ImageModel ImageField
IMAGE_FIELD_MAX_LENGTH = getattr(settings, 'PHOTOLOGUE_IMAGE_FIELD_MAX_LENGTH', 100)

# Path to sample image
SAMPLE_IMAGE_PATH = getattr(settings, 'PHOTOLOGUE_SAMPLE_IMAGE_PATH', os.path.join(
    os.path.dirname(__file__), 'res', 'sample.jpg'))

# Modify image file buffer size.
ImageFile.MAXBLOCK = getattr(settings, 'PHOTOLOGUE_MAXBLOCK', 256 * 2 ** 10)

# Photologue image path relative to media root
PHOTOLOGUE_DIR = getattr(settings, 'PHOTOLOGUE_DIR', 'photologue')

# Look for user function to define file paths
PHOTOLOGUE_PATH = getattr(settings, 'PHOTOLOGUE_PATH', None)
if PHOTOLOGUE_PATH is not None:
    if callable(PHOTOLOGUE_PATH):
        get_storage_path = PHOTOLOGUE_PATH
    else:
        parts = PHOTOLOGUE_PATH.split('.')
        module_name = '.'.join(parts[:-1])
        module = import_module(module_name)
        get_storage_path = getattr(module, parts[-1])
else:
    def get_storage_path(instance, filename):
        fn = unicodedata.normalize('NFKD', force_text(filename)).encode('ascii', 'ignore').decode('ascii')
        return os.path.join(PHOTOLOGUE_DIR, 'photos/groups', fn)

# Support CACHEDIR.TAG spec for backups for ignoring cache dir.
# See http://www.brynosaurus.com/cachedir/spec.html
PHOTOLOGUE_CACHEDIRTAG = os.path.join(PHOTOLOGUE_DIR, "photos", "cache", "CACHEDIR.TAG")
if not default_storage.exists(PHOTOLOGUE_CACHEDIRTAG):
    default_storage.save(PHOTOLOGUE_CACHEDIRTAG, ContentFile(
        "Signature: 8a477f597d28d172789f06886806bc55".encode('utf-8')))

# Exif Orientation values
# Value 0thRow	0thColumn
#   1	top     left
#   2	top     right
#   3	bottom	right
#   4	bottom	left
#   5	left	top
#   6	right   top
#   7	right   bottom
#   8	left    bottom

# Image Orientations (according to EXIF informations) that needs to be
# transposed and appropriate action
IMAGE_EXIF_ORIENTATION_MAP = {
    2: Image.FLIP_LEFT_RIGHT,
    3: Image.ROTATE_180,
    6: Image.ROTATE_270,
    8: Image.ROTATE_90,
}

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, _('Very Low')),
    (40, _('Low')),
    (50, _('Medium-Low')),
    (60, _('Medium')),
    (70, _('Medium-High')),
    (80, _('High')),
    (90, _('Very High')),
)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', _('Top')),
    ('right', _('Right')),
    ('bottom', _('Bottom')),
    ('left', _('Left')),
    ('center', _('Center (Default)')),
)

IMAGE_TRANSPOSE_CHOICES = (
    ('FLIP_LEFT_RIGHT', _('Flip left to right')),
    ('FLIP_TOP_BOTTOM', _('Flip top to bottom')),
    ('ROTATE_90', _('Rotate 90 degrees counter-clockwise')),
    ('ROTATE_270', _('Rotate 90 degrees clockwise')),
    ('ROTATE_180', _('Rotate 180 degrees')),
)

WATERMARK_STYLE_CHOICES = (
    ('tile', _('Tile')),
    ('scale', _('Scale')),
)

# Prepare a list of image filters
filter_names = []
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and \
            hasattr(klass, 'name'):
        filter_names.append(klass.__name__)
IMAGE_FILTERS_HELP_TEXT = _('Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE"'
                            '. Image filters will be applied in order. The following filters are available: %s.'
                            % (', '.join(filter_names)))

size_method_map = {}


class TagField(models.CharField):
    """Tags have been removed from Photologue, but the migrations still refer to them so this
    Tagfield definition is left here.
    """

    def __init__(self, **kwargs):
        default_kwargs = {'max_length': 255, 'blank': True}
        default_kwargs.update(kwargs)
        super(TagField, self).__init__(**default_kwargs)

    def get_internal_type(self):
        return 'CharField'


@python_2_unicode_compatible
class PhotoGroup(ImageModel):
    title = models.CharField(_('title'),
                             max_length=60)
    slug = models.SlugField(_('slug'),
                            unique=True,
                            max_length=250,
                            help_text=_('A "slug" is a unique URL-friendly title for an object.'))

    caption = models.TextField(_('caption'),
                               blank=True, max_length=1000)

    date_added = models.DateTimeField(_('date added'),
                                      default=now)

    is_public = models.BooleanField(_('is public'),
                                    default=True,
                                    help_text=_('Public photographs will be displayed in the default views.'))
    
    tags = TaggableManager(blank=True)

    owner = models.ForeignKey(User, null=True, blank=True, related_name='user_group_photos')

    url_image = models.URLField(max_length=255, default='', blank=True)

    thumbnail = models.ImageField(_('thumbnail'),
                                  upload_to=get_storage_path,
                                  null=True, blank=True)

    group = models.ForeignKey(UserGroups, related_name="group_photos")

    objects = PhotoQuerySet.as_manager()

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __str__(self):
        return self.title

    def save(self, created=True, *args, **kwargs):
        if created and not self.slug:
            self.slug = uuslug(self.title, instance=self)
            self.get_remote_image()
        super(PhotoGroup, self).save(*args, **kwargs)

    def get_remote_image(self):
        """
        Obtiene la url introducida por el usuario
        """

        if not self.image:
            return

        if self.url_image and not self.image:
            if len(self.url_image) > 255:
                raise ValueError('URL is very long.')

            else:
                domain, path = split_url(self.url_image)
                filename = get_url_tail(path)

                if not image_exists(self.url_image):
                    raise ValidationError(_("Couldn't retreive image. (There was an error reaching the server)"))

                fobject = retrieve_image(self.url_image)

                if not valid_image_mimetype(fobject):
                    raise ValidationError(_("Downloaded file was not a valid image"))

                pil_image = Image.open(fobject)
                pil_image.thumbnail((800, 600), Image.ANTIALIAS)

                if not valid_image_size(pil_image)[0]:
                    raise ValidationError(_("Image is too large (> 5mb)"))

                django_file = pil_to_django(pil_image)

                self.image.save(filename, django_file)

    def get_absolute_url(self):
        return reverse('photologue:pl-photo', args=[self.slug])

    def public_galleries(self):
        """Return the public galleries to which this photo belongs."""
        return self.galleries.filter(is_public=True)

    def get_previous_in_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        if not self.is_public:
            # raise ValueError('Cannot determine neighbours of a non-public photo.')
            return None
        photos = PhotoGroup.objects.filter(owner=self.owner, is_public=True)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        previous = None
        for photo in photos:
            if photo == self:
                return previous
            previous = photo
        return None

    def get_next_in_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        if not self.is_public:
            return None
            # raise ValueError('Cannot determine neighbours of a non-public photo.')
        photos = PhotoGroup.objects.filter(owner=self.owner, is_public=True)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        matched = False
        for photo in photos:
            if matched:
                return photo
            if photo == self:
                matched = True
        return None

    def get_previous_in_own_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        photos = PhotoGroup.objects.filter(owner=self.owner)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        previous = None
        for photo in photos:
            if photo == self:
                return previous
            previous = photo
        return None

    def get_next_in_own_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        photos = PhotoGroup.objects.filter(owner=self.owner)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        matched = False
        for photo in photos:
            if matched:
                return photo
            if photo == self:
                matched = True
        return None


def upload_video(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('photologue/videos/groups', filename)


def upload_thumbnail_video(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('photologue/videos/thumbnails/groups', filename)


class VideoGroup(models.Model):
    name = models.CharField(_('name'),
                            max_length=60)
    slug = models.SlugField(_('slug'),
                            unique=True,
                            max_length=250,
                            help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    caption = models.TextField(_('caption'),
                               blank=True, max_length=1000)
    is_public = models.BooleanField(_('is public'),
                                    default=True,
                                    help_text=_('Public photographs will be displayed in the default views.'))
    date_added = models.DateTimeField(_('date added'),
                                      default=now)
    tags = TaggableManager(blank=True)
    owner = models.ForeignKey(User, null=True, blank=True, related_name='user_group_videos')

    video = models.FileField(_('video'), upload_to=upload_video,
                             max_length=IMAGE_FIELD_MAX_LENGTH, validators=[validate_video])

    thumbnail = models.ImageField(_('thumbnail'), upload_to=upload_thumbnail_video, blank=True)

    group = models.ForeignKey(UserGroups, related_name="group_videos")

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _("video")
        verbose_name_plural = _("videos")

    @property
    def group_name(self):
        """
        Devuelve el nombre del canal para enviar notificaciones
        """
        return "videos-%s" % self.pk

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('photologue:pl-video', args=[self.slug])

    def save(self, created=True, *args, **kwargs):
        if created:
            self.slug = uuslug(str(self.owner_id) + self.name, instance=self)
        super(Video, self).save(*args, **kwargs)

    def get_previous_in_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        if not self.is_public:
            # raise ValueError('Cannot determine neighbours of a non-public photo.')
            return None
        photos = Video.objects.filter(owner=self.owner, is_public=True)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        previous = None
        for photo in photos:
            if photo == self:
                return previous
            previous = photo
        return None

    def get_next_in_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        if not self.is_public:
            return None
            # raise ValueError('Cannot determine neighbours of a non-public photo.')
        photos = Video.objects.filter(owner=self.owner, is_public=True)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        matched = False
        for photo in photos:
            if matched:
                return photo
            if photo == self:
                matched = True
        return None

    def get_previous_in_own_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        photos = Video.objects.filter(owner=self.owner)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        previous = None
        for photo in photos:
            if photo == self:
                return previous
            previous = photo
        return None

    def get_next_in_own_gallery(self):
        """Find the neighbour of this photo in the supplied publications_gallery.
        We assume that the publications_gallery and all its photos are on the same site.
        """
        photos = Video.objects.filter(owner=self.owner)
        if self not in photos:
            raise ValueError('Photo does not belong to publications_gallery.')
        matched = False
        for photo in photos:
            if matched:
                return photo
            if photo == self:
                matched = True
        return None




def add_default_site(instance, created, **kwargs):
    """
    Called via Django's signals when an instance is created.
    In case PHOTOLOGUE_MULTISITE is False, the current site (i.e.
    ``settings.SITE_ID``) will always be added to the site relations if none are
    present.
    """
    if not created:
        return
    if getattr(settings, 'PHOTOLOGUE_MULTISITE', False):
        return
    if instance.sites.exists():
        return
    instance.sites.add(Site.objects.get_current())


def generate_thumb(instance, created, **kwargs):
    """
    Generamos thumbnail
    """
    if created:
        generate_thumbnails.delay(instance=instance.pk)


def generate_video_thumb(instance, created, **kwargs):
    """
    Generamos thumbnail para video
    :param instance: Video
    :param created: Si es creado o actualizado
    :param kwargs:
    :return:
    """
    if created:
        generate_video_thumbnail.delay(instance=instance.pk)


post_save.connect(add_default_site, sender=PhotoGroup)
post_save.connect(generate_thumb, sender=PhotoGroup)
post_save.connect(generate_video_thumb, sender=VideoGroup)
