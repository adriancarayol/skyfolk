import json
import os

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import publications_groups
from notifications.signals import notify
from publications.utils import convert_avi_to_mp4
from skyfolk.celery import app
from .models import PublicationGroupVideo, PublicationGroup

logger = get_task_logger(__name__)


@app.task(name='tasks.process_group_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationGroup.objects.select_related('board_group').get(id=publication_id)
        group = publication.board_group
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    video_file, media_path = publications_groups.utils.generate_path_video()

    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))

    convert_avi_to_mp4(file, video_file)
    PublicationGroupVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)

    logger.info('VIDEO CONVERTED')

    if user_id:
        user = User.objects.get(id=user_id)
        notify.send(user, actor=user.username, recipient=user,
                    verb=u'¡Ya esta tu video %s!' % filename,
                    immediately=True,
                    description='<a href="%s/%d/">Ver</a>' % ('/publication/group/detail', publication_id))

        data = {
            'type': "video",
            'video': media_path,
            'id': publication_id
        }

        Channel_group(group.group_channel).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(name='tasks.process_group_pub_gif')
def process_gif_publication(file, publication_id, filename, user_id=None):
    try:
        publication = PublicationGroup.objects.select_related('board_group').get(id=publication_id)
        group = publication.board_group
    except ObjectDoesNotExist:
        logger.info('Publication does not exist')
        return

    clip = mp.VideoFileClip(file)
    video_file, media_path = publications_groups.utils.generate_path_video()

    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))

    clip.write_videofile(video_file, threads=2)
    PublicationGroupVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)

    logger.info('GIF CONVERTED')

    if user_id:
        user = User.objects.get(id=user_id)
        notify.send(user, actor=user.username, recipient=user,
                    verb=u'¡Ya esta tu video %s!' % filename,
                    immediately=True,
                    description='<a href="%s/%d/">Ver</a>' % ('/publication/group/detail', publication_id))

        data = {
            'type': "video",
            'video': media_path,
            'id': publication_id
        }

        Channel_group(group.group_channel).send({
            "text": json.dumps(data)
        }, immediately=True)
