import json
import os
import uuid

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from notifications.models import Notification

import publications_groups
from publications.utils import convert_avi_to_mp4
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import PublicationThemeVideo, PublicationTheme

logger = get_task_logger(__name__)


def generate_path_video(ext='mp4'):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return [os.path.join('skyfolk/media/theme_publications/videos', filename),
            os.path.join('theme_publications/videos', filename)]


@app.task(name='tasks.process_theme_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationTheme.objects.select_related('board_theme').get(id=publication_id)
        theme = publication.board_theme
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    video_file, media_path = generate_path_video()

    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))

    convert_avi_to_mp4(file, video_file)
    PublicationThemeVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)

    logger.info('VIDEO CONVERTED')

    if user_id:
        user = User.objects.get(id=user_id)
        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
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
            'video': media_path,
            'id': publication_id
        }

        Channel_group(notification_channel(user.id)).send({
            "text": json.dumps({'content': content})
        }, immediately=True)

        Channel_group(theme.theme_channel).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(name='tasks.process_theme_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationTheme.objects.select_related('board_theme').get(id=publication_id)
        theme = publication.board_theme
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    clip = mp.VideoFileClip(file)
    video_file, media_path = generate_path_video()

    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))

    clip.write_videofile(video_file, threads=2)
    PublicationThemeVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)

    logger.info('GIF CONVERTED')

    if user_id:
        user = User.objects.get(id=user_id)
        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
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
            'video': media_path,
            'id': publication_id
        }

        Channel_group(notification_channel(user.id)).send({
            "text": json.dumps({'content': content})
        }, immediately=True)

        Channel_group(theme.theme_channel).send({
            "text": json.dumps(data)
        }, immediately=True)
