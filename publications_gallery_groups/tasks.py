import json
import os
import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.template.loader import render_to_string
from django.urls import reverse_lazy
import publications_gallery_groups
from notifications.models import Notification
from publications.utils import convert_video_to_mp4
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import PublicationPhotoVideo, PublicationGroupMediaPhoto, PublicationGroupMediaVideo, PublicationVideoVideo
from django.db import IntegrityError
from asgiref.sync import async_to_sync

logger = get_task_logger(__name__)
channel_layer = get_channel_layer()

get_channel_video_name = lambda id: "group-video-pub-{}".format(id)


@app.task(ignore_result=True, name='tasks.process_group_photo_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None

    user = User.objects.get(id=user_id)

    try:
        publication = PublicationGroupMediaPhoto.objects.get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return

    mp4_path = "{0}{1}".format(file, '.mp4')
    convert_video_to_mp4(file, mp4_path)

    pub = PublicationPhotoVideo.objects.create(publication_id=publication_id)

    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)

        logger.info('VIDEO CONVERTED')

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
            'video': pub.video.url,
            'id': publication_id
        }

        async_to_sync(channel_layer.group_send)(notification_channel(user.id), {
            'type': 'new_notification',
            "message": {
                'content': content
            }
        })

        for id in publication.get_ancestors().values_list('id', flat=True):
            async_to_sync(channel_layer.group_send)(publications_gallery_groups.utils.get_channel_name(id), {
                'type': 'new_publication',
                "message": data
            })

        async_to_sync(channel_layer.group_send)(photo.group_name, {
            'type': 'new_publication',
            "message": data
        })
    except Exception as e:
        logger.info('ERROR: {}'.format(e))
        pub.delete()
    finally:
        os.remove(file)


@app.task(ignore_result=True, name='tasks.process_group_photo_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationGroupMediaPhoto.objects.select_related('board_photo').get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return

    clip = mp.VideoFileClip(file)
    mp4_path = "{0}{1}".format(file, '.mp4')
    clip.write_videofile(mp4_path, threads=2)

    pub = PublicationPhotoVideo.objects.create(publication_id=publication_id)

    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)
        logger.info('GIF CONVERTED')

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
            'video': pub.video.url,
            'id': publication_id
        }

        async_to_sync(channel_layer.group_send)(notification_channel(user.id), {
            'type': 'new_notification',
            "message": {
                'content': content
            }
        })

        for id in publication.get_ancestors().values_list('id', flat=True):
            async_to_sync(channel_layer.group_send)(publications_gallery_groups.utils.get_channel_name(id), {
                'type': 'new_publication',
                "message": data
            })

        async_to_sync(channel_layer.group_send)(photo.group_name, {
            'type': 'new_publication',
            "message": data
        })
    except Exception as e:
        logger.info('ERROR: {}'.format(e))
        pub.delete()
    finally:
        os.remove(file)


# Video tasks
@app.task(ignore_result=True, name='tasks.process_group_video_pub_video')
def process_video_video_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationGroupMediaVideo.objects.get(id=publication_id)
        video = publication.board_video
    except ObjectDoesNotExist:
        return

    mp4_path = "{0}{1}".format(file, '.mp4')
    convert_video_to_mp4(file, mp4_path)

    pub = PublicationVideoVideo.objects.create(publication_id=publication_id)
    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)

        logger.info('VIDEO CONVERTED')

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="{0}">Ver</a>'.format(reverse_lazy(
                                                           'publications_gallery_groups:publication_video_detail',
                                                           args=[publication_id])))
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
            'type': 'new_notification',
            "message": {
                'content': content
            }
        })

        for id in publication.get_ancestors().values_list('id', flat=True):
            async_to_sync(channel_layer.group_send)(get_channel_video_name(id), {
                'type': 'new_publication',
                "message": data
            })

        async_to_sync(channel_layer.group_send)(video.group_name, {
            'type': 'new_publication',
            "message": data
        })
    except Exception as e:
        logger.info('ERROR: {}'.format(e))
        pub.delete()
    finally:
        os.remove(file)


@app.task(ignore_result=True, name='tasks.process_group_video_pub_gif')
def process_gif_video_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationGroupMediaVideo.objects.get(id=publication_id)
        video = publication.board_video
    except ObjectDoesNotExist:
        return

    clip = mp.VideoFileClip(file)
    mp4_path = "{0}{1}".format(file, '.mp4')
    clip.write_videofile(mp4_path, threads=2)

    pub = PublicationVideoVideo.objects.create(publication_id=publication_id)

    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)

        logger.info('GIF CONVERTED')

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="{0}">Ver</a>'.format(reverse_lazy(
                                                           'publications_gallery_groups:publication_video_detail',
                                                           args=[publication_id])))
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
            'type': 'new_notification',
            "message": {
                'content': content
            }
        })

        for id in publication.get_ancestors().values_list('id', flat=True):
            async_to_sync(channel_layer.group_send)(get_channel_video_name(id), {
                'type': 'new_publication',
                "message": data
            })

        async_to_sync(channel_layer.group_send)(video.group_name, {
            'type': 'new_publication',
            "message": data
        })
    except Exception as e:
        logger.info('ERROR: {}'.format(e))
        pub.delete()
    finally:
        os.remove(file)
