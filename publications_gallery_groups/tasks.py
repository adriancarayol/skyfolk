import json
import os
import uuid
import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse_lazy

import publications_gallery_groups
from notifications.models import Notification
from publications.utils import convert_video_to_mp4
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import PublicationPhotoVideo, PublicationGroupMediaPhoto, PublicationGroupMediaVideo, PublicationVideoVideo
from django.db import IntegrityError

logger = get_task_logger(__name__)

generate_path_video = lambda filename, ext: (
    [os.path.join('skyfolk/media/photo_publications/videos', str(filename) + ext),
     os.path.join('photo_publications/videos', str(filename) + ext)])

get_channel_video_name = lambda id: "group-video-pub-{}".format(id)


@app.task(ignore_result=True, name='tasks.process_group_photo_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationGroupMediaPhoto.objects.get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return

    video_file, media_path = generate_path_video(uuid.uuid4(), ".mp4")
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
                                                       description='<a href="{0}">Ver</a>'.format(reverse_lazy(
                                                           'publications_gallery_groups:publication_photo_detail',
                                                           args=[publication_id])))
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

        [Channel_group(publications_gallery_groups.utils.get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(photo.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(ignore_result=True, name='tasks.process_group_photo_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationGroupMediaPhoto.objects.select_related('board_photo').get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return

    clip = mp.VideoFileClip(file)
    video_file, media_path = generate_path_video(uuid.uuid4(), ".mp4")
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
                                                       description='<a href="{0}">Ver</a>'.format(reverse_lazy(
                                                           'publications_gallery_groups:publication_photo_detail',
                                                           args=[publication_id])))
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

        [Channel_group(publications_gallery_groups.utils.get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(photo.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)


# Video tasks

@app.task(ignore_result=True, name='tasks.process_group_video_pub_video')
def process_video_video_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationGroupMediaVideo.objects.get(id=publication_id)
        video = publication.board_video
    except ObjectDoesNotExist:
        return

    video_file, media_path = generate_path_video(uuid.uuid4(), ".mp4")
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    convert_video_to_mp4(file, video_file)
    PublicationVideoVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('VIDEO CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="{0}">Ver</a>'.format(reverse_lazy(
                                                           'publications_gallery_groups:video/publication/detail/',
                                                           args=[publication_id])))
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

        [Channel_group(get_channel_video_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(video.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(ignore_result=True, name='tasks.process_group_video_pub_gif')
def process_gif_video_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationGroupMediaVideo.objects.get(id=publication_id)
        video = publication.board_video
    except ObjectDoesNotExist:
        return
    clip = mp.VideoFileClip(file)
    video_file, media_path = generate_path_video(uuid.uuid4(), ".mp4")
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    clip.write_videofile(video_file, threads=2)
    PublicationVideoVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('GIF CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="{0}">Ver</a>'.format(reverse_lazy(
                                                           'publications_gallery_groups:video/publication/detail/',
                                                           args=[publication_id])))
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

        [Channel_group(get_channel_video_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(video.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)
