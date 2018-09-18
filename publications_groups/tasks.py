import json
import os

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import IntegrityError
from django.template.loader import render_to_string
from notifications.models import Notification
import publications_groups
from publications.utils import convert_video_to_mp4
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import PublicationGroupVideo, PublicationGroup

logger = get_task_logger(__name__)
channel_layer = get_channel_layer()


@app.task(name='tasks.process_group_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationGroup.objects.select_related('board_group').get(id=publication_id)
        group = publication.board_group
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    mp4_path = "{0}{1}".format(file, '.mp4')
    convert_video_to_mp4(file, mp4_path)

    pub = PublicationGroupVideo.objects.create(publication_id=publication_id)

    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)

        logger.info('VIDEO CONVERTED')

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="%s">Ver</a>' % (
                                                               '/publication/group/detail/' + str(publication_id)))
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

        Channel_group(notification_channel(user.id)).send({
            "text": json.dumps({'content': content})
        }, immediately=True)

        [Channel_group(publications_groups.utils.get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(group.group_channel).send({
            "text": json.dumps(data)
        }, immediately=True)
    except Exception as e:
        pub.delete()
        logger.info('ERROR {}'.format(e))
    finally:
        os.remove(file)


@app.task(name='tasks.process_group_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    assert user_id is not None
    assert publication_id is not None
    user = User.objects.get(id=user_id)

    try:
        publication = PublicationGroup.objects.select_related('board_group').get(id=publication_id)
        group = publication.board_group
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    clip = mp.VideoFileClip(file)

    mp4_path = "{0}{1}".format(file, '.mp4')

    clip.write_videofile(mp4_path, threads=2)
    pub = PublicationGroupVideo.objects.create(publication_id=publication_id)

    try:
        with open(mp4_path, 'rb') as f:
            pub.video.save("video.mp4", File(f), True)
        logger.info('GIF CONVERTED')

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                       verb=u'¡Ya esta tu video %s!' % filename,
                                                       description='<a href="%s">Ver</a>' % (
                                                               '/publication/group/detail/' + str(publication_id)))
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

        Channel_group(notification_channel(user.id)).send({
            "text": json.dumps({'content': content})
        }, immediately=True)

        [Channel_group(publications_groups.utils.get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in publication.get_ancestors().values_list('id', flat=True)]

        Channel_group(group.group_channel).send({
            "text": json.dumps(data)
        }, immediately=True)
    except Exception as e:
        pub.delete()
        logger.info('ERROR {}'.format(e))
    finally:
        os.remove(file)
