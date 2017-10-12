import tempfile
import io
import os

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from publications.exceptions import CantOpenMedia, MediaNotSupported
from publications_groups.themes.models import PublicationThemeVideo, PublicationThemeImage
from publications_groups.utils import check_image_property
from .tasks import process_gif_publication, process_video_publication


def optimize_publication_media(instance, image_upload, exts):
    if image_upload:
        for index, media in enumerate(image_upload):
            try:
                if exts[index][0] == "video":  # es un video
                    if exts[index][1] == 'mp4':
                        PublicationThemeVideo.objects.create(publication=instance,
                                                             video=media)
                    else:
                        tmp = tempfile.NamedTemporaryFile(delete=False)
                        for block in media.chunks():
                            tmp.write(block)
                        process_video_publication.delay(tmp.name, instance.id, media.name, instance.author.id)
                elif exts[index][0] == "image" and exts[index][1] == "gif":  # es un gif
                    tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
                    for block in media.chunks():
                        tmp.write(block)
                    process_gif_publication.delay(tmp.name, instance.id, media.name, instance.author.id)
                else:  # es una imagen normal
                    try:
                        image = Image.open(media)
                    except IOError:
                        raise CantOpenMedia(u'No podemos procesar el archivo {image}'.format(image=media.name))

                    fill_color = (255, 255, 255, 0)
                    if image.mode in ('RGBA', 'LA'):
                        background = Image.new(image.mode[:-1], image.size, fill_color)
                        background.paste(image, image.split()[-1])
                        image = background
                    image.thumbnail((800, 600), Image.ANTIALIAS)
                    output = io.BytesIO()
                    image.save(output, format='JPEG', optimize=True, quality=70)
                    output.seek(0)
                    photo = InMemoryUploadedFile(output, None, "%s.jpeg" % os.path.splitext(media.name)[0],
                                                 'image/jpeg', output.tell(), None)
                    PublicationThemeImage.objects.create(publication=instance, image=photo)
            except IndexError:
                raise MediaNotSupported(u'No podemos procesar este tipo de archivo {file}.'.format(file=media.name))
