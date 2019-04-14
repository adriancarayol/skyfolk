import os
import uuid
from tempfile import NamedTemporaryFile
from io import BytesIO

from PIL import Image
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

import photologue

from skyfolk.celery import app
from utils.media import create_thumbnail_video
from django.core.files.storage import default_storage


def flat(*nums):
    "Build a tuple of ints from float or integer arguments. Useful because PIL crop and resize require integer points."

    return tuple(int(round(n)) for n in nums)


class Size(object):
    def __init__(self, pair):
        self.width = float(pair[0])
        self.height = float(pair[1])

    @property
    def aspect_ratio(self):
        return self.width / self.height

    @property
    def size(self):
        return flat(self.width, self.height)


def cropped_thumbnail(img, size):
    """
    Builds a thumbnail by cropping out a maximal region from the center of the original with
    the same aspect ratio as the target size, and then resizing. The result is a thumbnail which is
    always EXACTLY the requested size and with no aspect ratio distortion (although two edges, either
    top/bottom or left/right depending whether the image is too tall or too wide, may be trimmed off.)
    """
    img = Image.open(img.image).convert("RGBA")
    original = Size(img.size)
    target = Size(size)

    if target.aspect_ratio > original.aspect_ratio:
        # image is too tall: take some off the top and bottom
        scale_factor = target.width / original.width
        crop_size = Size((original.width, target.height / scale_factor))
        top_cut_line = (original.height - crop_size.height) / 2
        img = img.crop(
            flat(0, top_cut_line, crop_size.width, top_cut_line + crop_size.height)
        )
    elif target.aspect_ratio < original.aspect_ratio:
        # image is too wide: take some off the sides
        scale_factor = target.height / original.height
        crop_size = Size((target.width / scale_factor, original.height))
        side_cut_line = (original.width - crop_size.width) / 2
        img = img.crop(
            flat(side_cut_line, 0, side_cut_line + crop_size.width, crop_size.height)
        )

    return img.resize(target.size, Image.ANTIALIAS)


@app.task(name="tasks.generate_photo_thumbnail")
def generate_thumbnails(instance):
    exist_photo = True

    try:
        photo_to_crop = photologue.models.Photo.objects.get(pk=instance)
    except ObjectDoesNotExist:
        exist_photo = False
        photo_to_crop = None

    if exist_photo and photo_to_crop.image:  # Si la foto existe
        thumb = cropped_thumbnail(photo_to_crop, flat(300.0, 300.0))
        tempfile_io = BytesIO()
        thumb.save(tempfile_io, format="PNG")
        tempfile_io.seek(0, os.SEEK_END)
        image_file = InMemoryUploadedFile(
            tempfile_io, None, "thumb.png", "image/png", tempfile_io.tell(), None
        )
        photo_to_crop.thumbnail.save(str(uuid.uuid4()) + "thumb.png", image_file)
        photo_to_crop.save()


@app.task(name="tasks.generate_video_thumbnail")
def generate_video_thumbnail(instance):
    import shutil

    exist_video = True

    try:
        video = photologue.models.Video.objects.get(pk=instance)
    except ObjectDoesNotExist:
        exist_video = False
        video = None

    if exist_video and video.video:
        thumb_tmp = NamedTemporaryFile()
        local_video = default_storage.open(File(video.video).name, "rb")
        tmp_video = NamedTemporaryFile()
        shutil.copyfileobj(local_video, tmp_video, 1024)
        tmp_video.seek(0)

        create_thumbnail_video(tmp_video.name, thumb_tmp.name)
        video.thumbnail.save(str(uuid.uuid4()) + "thumbnail.jpg", thumb_tmp, save=True)
