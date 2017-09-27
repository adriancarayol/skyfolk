import json
import os

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string

import publications_gallery
from notifications.models import Notification
from publications.utils import convert_video_to_mp4
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import PublicationPhotoVideo, PublicationPhoto
from django.db import IntegrityError

logger = get_task_logger(__name__)


@app.task(ignore_result=True, name='tasks.process_photo_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationPhoto.objects.get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return

    video_file, media_path = publications_gallery.utils.generate_path_video()
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    convert_video_to_mp4(file, video_file)
    PublicationPhotoVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('VIDEO CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="%s">Ver</a>' % (
                                                           '/publication_pdetail/' + str(publication_id)))
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

        [Channel_group(publications_gallery.utils.get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(photo.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(ignore_result=True, name='tasks.process_photo_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationPhoto.objects.get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return
    clip = mp.VideoFileClip(file)
    video_file, media_path = publications_gallery.utils.generate_path_video()
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    clip.write_videofile(video_file, threads=2)
    PublicationPhotoVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('GIF CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                   verb=u'¡Ya esta tu video %s!' % filename,
                                                   description='<a href="%s">Ver</a>' % (
                                                       '/publication_pdetail/' + str(publication_id)))
        except IntegrityError as e:
            logger.info(e)
            #TODO: Enviar mensaje al user con el error
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

        [Channel_group(publications_gallery.utils.get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(photo.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)
