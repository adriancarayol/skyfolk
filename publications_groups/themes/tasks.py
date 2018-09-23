import json
import os
import uuid

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.conf import settings
from notifications.models import Notification
from asgiref.sync import async_to_sync
from publications.utils import convert_video_to_mp4
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import PublicationThemeVideo, PublicationTheme

logger = get_task_logger(__name__)

channel_layer = get_channel_layer()


def generate_path_video(username, ext='mp4'):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    filename = "%s.%s" % (uuid.uuid4(), ext)
    path = os.path.join(settings.MEDIA_URL, 'theme_publications/videos')
    full_path = os.path.join(path, username)

    return os.path.join(full_path, filename)


@app.task(name='tasks.process_theme_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationTheme.objects.select_related('board_theme').get(id=publication_id)
        theme = publication.board_theme
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    mp4_path = "{0}{1}".format(file, '.mp4')
    convert_video_to_mp4(file, mp4_path)
    pub = PublicationThemeVideo.objects.create(publication_id=publication_id)

    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)

        logger.info('VIDEO CONVERTED')

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'Ya esta tu video %s' % filename,
                                                       description='<a href="{0}">Ver</a>'.format(
                                                           reverse_lazy('user_groups:group_theme',
                                                                        kwargs={'slug': theme.slug})))
        except IntegrityError as e:
            logger.info(e)
            # TODO: Enviar mensaje al user con el error
            return

        content = render_to_string(template_name='channels/new_notification.html',
                                   context={'notification': notification})

        data = {
            'type': "video",
            'video': pub.video.url,
            'id': publication_id
        }

        async_to_sync(channel_layer.group_send)(notification_channel(user.id), {
            'type': 'new_publication',
            "message": {
                'content': content
            }
        })

        async_to_sync(channel_layer.group_send)(theme.theme_channel, {
            'type': 'new_publication',
            "message": data
        })
    except Exception as e:
        pub.delete()
        logger.info('ERROR: {}'.format(e))
    finally:
        os.remove(file)


@app.task(name='tasks.process_theme_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationTheme.objects.select_related('board_theme').get(id=publication_id)
        theme = publication.board_theme
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    clip = mp.VideoFileClip(file)
    mp4_path = "{0}{1}".format(file, '.mp4')

    clip.write_videofile(mp4_path, threads=2)

    pub = PublicationThemeVideo.objects.create(publication_id=publication_id)

    try:
        logger.info('GIF CONVERTED')

        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb='Ya esta tu video {0}'.format(filename),
                                                       description='<a href="{0}">Ver</a>'.format(
                                                           reverse_lazy('user_groups:group_theme',
                                                                        kwargs={'slug': theme.slug})))
        except IntegrityError as e:
            logger.info(e)
            # TODO: Enviar mensaje al user con el error
            return

        content = render_to_string(template_name='channels/new_notification.html',
                                   context={'notification': notification})

        data = {
            'type': "video",
            'video': pub.video.url,
            'id': publication_id
        }

        async_to_sync(channel_layer.group_send)(notification_channel(user.id), {
            'type': 'new_publication',
            "message": {
                'content': content
            }
        })

        async_to_sync(channel_layer.group_send)(notification_channel(user.id), {
            'type': 'new_publication',
            "message": data
        })
    except Exception as e:
        pass
    finally:
        os.remove(file)
