import io
import os
import tempfile
import uuid

import magic
import publications_gallery

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from publications.exceptions import CantOpenMedia, SizeIncorrect, MaxFilesReached, MediaNotSupported
from .tasks import process_gif_publication, process_video_publication

def check_image_property(image):
    if not image:
        raise CantOpenMedia(u'No podemos procesar el archivo {image}'.format(image=image.name))
    if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
        raise SizeIncorrect(
            u"Sólo se permiten archivos de hasta 5MB. ({image} tiene {size}B)".format(image=image.name,
                                                                                      size=image._size))


def check_num_images(image_collection):
    if len(image_collection) > 5:
        raise MaxFilesReached(u'Sólo se permiten 5 archivos por publicación.')


def optimize_publication_media(instance, image_upload):
    check_num_images(image_upload)
    content_video = False
    if image_upload:
        for index, media in enumerate(image_upload):
            check_image_property(media)
            f = magic.Magic(mime=True, uncompress=True)
            file_type = f.from_buffer(media.read(1024)).split('/')
            try:
                if file_type[0] == "video":  # es un video
                    if file_type[1] == 'mp4':
                        publications_gallery.models.PublicationPhotoVideo.objects.create(publication=instance, video=media)
                    else:
                        tmp = tempfile.NamedTemporaryFile(delete=False)
                        for block in media.chunks():
                            tmp.write(block)
                        process_video_publication.delay(tmp.name, instance.id, media.name, instance.p_author.id)
                    content_video = True
                elif file_type[0] == "image" and file_type[1] == "gif":  # es un gif
                    tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
                    for block in media.chunks():
                        tmp.write(block)
                    process_gif_publication.delay(tmp.name, instance.id, media.name, instance.p_author.id)
                    content_video = True
                else:  # es una imagen normal
                    try:
                        image = Image.open(media)
                    except IOError:
                        raise CantOpenMedia(u'No podemos procesar el archivo {image}'.format(image=media.name))
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    image.thumbnail((800, 600), Image.ANTIALIAS)
                    output = io.BytesIO()
                    image.save(output, format='JPEG', optimize=True, quality=70)
                    output.seek(0)
                    photo = InMemoryUploadedFile(output, None, "%s.jpeg" % os.path.splitext(media.name)[0],
                                                 'image/jpeg', output.tell(), None)
                    publications_gallery.models.PublicationPhotoImage.objects.create(publication=instance, image=photo)
            except IndexError:
                raise MediaNotSupported(u'No podemos procesar este tipo de archivo {file}.'.format(file=media.name))
    return content_video

def generate_path_video(ext='mp4'):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return [os.path.join('skyfolk/media/photo_publications/videos', filename), os.path.join('photo_publications/videos', filename)]