import io
import os
import tempfile
import uuid

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

import publications_gallery
from publications.exceptions import (
    CantOpenMedia,
    SizeIncorrect,
    MaxFilesReached,
    MediaNotSupported,
)
from .tasks import process_gif_publication, process_video_publication


def get_channel_name(id):
    """
    Devuelve el nombre del blog para
    una publicacion en la galeria
    :param id: ID de la publicacion
    :return:
    """
    return "photo-pub-%s" % id


def check_image_property(image):
    if not image:
        raise CantOpenMedia(
            u"No podemos procesar el archivo {image}".format(image=image.name)
        )
    if image.size > settings.BACK_IMAGE_DEFAULT_SIZE:
        raise SizeIncorrect(
            u"Sólo se permiten archivos de hasta 5MB. ({image} tiene {size}B)".format(
                image=image.name, size=image.size
            )
        )


def check_num_images(image_collection):
    if len(image_collection) > 5:
        raise MaxFilesReached(u"Sólo se permiten 5 archivos por publicación.")


def optimize_publication_media(instance, image_upload, exts):
    if image_upload:
        for index, media in enumerate(image_upload):
            try:
                if exts[index][0] == "video":  # es un video
                    if exts[index][1] == "mp4":
                        publications_gallery.models.PublicationPhotoVideo.objects.create(
                            publication=instance, video=media
                        )
                    else:
                        tmp = tempfile.NamedTemporaryFile(delete=False)
                        for block in media.chunks():
                            tmp.write(block)
                        process_video_publication.delay(
                            tmp.name, instance.id, media.name, instance.author.id
                        )
                elif exts[index][0] == "image" and exts[index][1] == "gif":  # es un gif
                    tmp = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
                    for block in media.chunks():
                        tmp.write(block)
                    process_gif_publication.delay(
                        tmp.name, instance.id, media.name, instance.author.id
                    )
                else:  # es una imagen normal
                    try:
                        image = Image.open(media).convert("RGBA")
                    except IOError:
                        raise CantOpenMedia(
                            u"No podemos procesar el archivo {image}".format(
                                image=media.name
                            )
                        )

                    fill_color = (255, 255, 255, 0)
                    if image.mode in ("RGBA", "LA"):
                        background = Image.new(image.mode[:-1], image.size, fill_color)
                        background.paste(image, image.split()[-1])
                        image = background
                    image.thumbnail((800, 600), Image.ANTIALIAS)
                    output = io.BytesIO()
                    image.save(output, format="JPEG", optimize=True, quality=70)
                    output.seek(0)
                    photo = InMemoryUploadedFile(
                        output,
                        None,
                        "%s.jpeg" % os.path.splitext(media.name)[0],
                        "image/jpeg",
                        output.tell(),
                        None,
                    )
                    publications_gallery.models.PublicationPhotoImage.objects.create(
                        publication=instance, image=photo
                    )
            except IndexError:
                raise MediaNotSupported(
                    u"No podemos procesar este tipo de archivo {file}.".format(
                        file=media.name
                    )
                )


def generate_path_video(username, ext="mp4"):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    filename = "%s.%s" % (uuid.uuid4(), ext)
    path = os.path.join(settings.MEDIA_URL, "photo_publications/videos")
    full_path = os.path.join(path, username)

    return os.path.join(full_path, filename)


def get_photo_channel(photo_id):
    """
    Devuelve el nombre del canal para enviar notificaciones
    """
    return "photos-%s" % photo_id
