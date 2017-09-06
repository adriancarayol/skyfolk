import json
import os

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from publications.models import Publication, PublicationDeleted
from publications_gallery.models import PublicationPhoto
from skyfolk.celery import app
from user_profile.utils import group_name, notification_channel
from .models import PublicationVideo
from .utils import generate_path_video, convert_avi_to_mp4
from notifications.models import Notification
from django.db import IntegrityError

logger = get_task_logger(__name__)


@app.task(name='tasks.clean_deleted_publications')
def clean_deleted_publications():
    logger.info('Finding deleted publications...')
    publications = Publication.objects.filter(deleted=True)
    publications_contains_shared = publications.values_list('id', flat=True)
    pubs_shared = Publication.objects.filter(shared_publication__id__in=publications_contains_shared)

    for publication in publications:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.author, content=publication.content,
                                                                created=publication.created)
        extra_content = publication.has_extra_content()
        if extra_content:
            publication.extra_content.delete()

        logger.info('Deleting images...')
        for img in publication.images.all():
            if img.image:
                if os.path.isfile(img.image.path):
                    os.remove(img.image.path)
            img.delete()
            logger.info('Image deleted')
        for vid in publication.videos.all():
            if vid.image:
                if os.path.isfile(vid.video.path):
                    os.remove(vid.video.path)
                vid.delete()
            logger.info('Image deleted')
        publication.delete()
        logger.info("Publication safe deleted {}".format(pub.id))
    # Eliminamos publicaciones que referencien
    # a una publicacion compartida eliminada
    for publication in pubs_shared:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.author, content=publication.content,
                                                                created=publication.created)
        extra_content = publication.has_extra_content()
        if extra_content:
            publication.extra_content.delete()
        publication.delete()


@app.task(name='tasks.clean_deleted_photo_publications')
def clean_deleted_photo_publications():
    logger.info('Finding deleted publications...')
    publications = PublicationPhoto.objects.filter(deleted=True)
    publications_contains_shared = publications.values_list('id', flat=True)
    pubs_shared = Publication.objects.filter(shared_photo_publication__id__in=publications_contains_shared)

    for publication in publications:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.p_author,
                                                                content=publication.content,
                                                                created=publication.created, type_publication=2)
        extra_content = publication.has_extra_content()
        if extra_content:
            publication.publication_photo_extra_content.delete()

        logger.info('Deleting images...')
        for img in publication.images.all():
            if img.image:
                if os.path.isfile(img.image.path):
                    os.remove(img.image.path)
            img.delete()
            logger.info('Image deleted')
        for vid in publication.videos.all():
            if vid.image:
                if os.path.isfile(vid.video.path):
                    os.remove(vid.video.path)
                vid.delete()
            logger.info('Image deleted')
        publication.delete()
        logger.info("Publication safe deleted {}".format(pub.id))

    for publication in pubs_shared:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.p_author,
                                                                content=publication.content,
                                                                created=publication.created, type_publication=2)
        extra_content = publication.has_extra_content()
        if extra_content:
            publication.extra_content.delete()
        publication.delete()


@app.task(ignore_result=True, name='tasks.process_video')
def process_video_publication(file, publication_id, filename, user_id=None,
                              board_owner_id=None):
    logger.info('ENTERING PROCESS VIDEO')
    video_file, media_path = generate_path_video()
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    convert_avi_to_mp4(file, video_file)
    PublicationVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('VIDEO CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                   verb=u'¡Ya esta tu video %s!' % filename,
                                                   description='<a href="%s">Ver</a>' % (
                                                       '/publication/' + str(publication_id)))
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

        if board_owner_id:
            Channel_group(group_name(board_owner_id)).send({
                "text": json.dumps(data)
            }, immediately=True)


@app.task(ignore_result=True, name='tasks.process_gif')
def process_gif_publication(file, publication_id, filename, user_id=None,
                            board_owner_id=None):
    logger.info('ENTERING PROCESS GIF')
    clip = mp.VideoFileClip(file)
    video_file, media_path = generate_path_video()
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    clip.write_videofile(video_file, threads=2)
    PublicationVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('GIF CONVERTED')

    if user_id:
        user = User.objects.get(id=user_id)

        try:
            notification = Notification.objects.create(actor=user, recipient=user,
                                                   verb=u'¡Ya esta tu video %s!' % filename,
                                                   description='<a href="%s">Ver</a>' % (
                                                       '/publication/' + str(publication_id)))
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

        if board_owner_id:
            Channel_group(group_name(board_owner_id)).send({
                "text": json.dumps(data)
            }, immediately=True)
