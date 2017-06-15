import json
import os

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.forms import model_to_dict

from notifications.models import Notification
from skyfolk.celery import app
from user_profile.utils import notification_channel
from .models import Publication, PublicationDeleted
from .models import PublicationVideo
from .utils import generate_path_video, convert_avi_to_mp4

logger = get_task_logger(__name__)


@app.task(name='tasks.clean_deleted_publications')
def clean_deleted_publications():
    logger.info('Finding deleted publications...')
    publications = Publication.objects.filter(deleted=True)
    for publication in publications:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.author, content=publication.content,
                                                                created=publication.created)
        extra_content = publication.extra_content
        shared = publication.shared_publication
        if extra_content:
            extra_content.delete()
        if shared:
            shared.publication.shared -= 1
            shared.publication.save()
            shared.delete()

        logger.info('Deleting images...')
        for img in publication.images.all():
            if img.image:
                if os.path.isfile(img.image.path):
                    os.remove(img.image.path)
            img.delete()
            logger.info('Image deleted')
        publication.delete()
        logger.info("Publication safe deleted {}".format(pub.id))


@app.task(name='tasks.process_video')
def process_video_publication(file, publication_id, user_id=None):
    video_file, media_path = generate_path_video()
    convert_avi_to_mp4(file, video_file)
    PublicationVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('VIDEO CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        newnotify = Notification.objects.create(actor=user, recipient=user, verb=u'¡tu publicación está lista!',
                                                description='<a href="%s">Ver</a>' % (
                                                    '/publication/' + str(publication_id)))
        data = model_to_dict(newnotify)
        if newnotify.actor:
            data['actor'] = str(newnotify.actor)
        if newnotify.target:
            data['target'] = str(newnotify.target)
        if newnotify.action_object:
            data['action_object'] = str(newnotify.action_object)
        if newnotify.slug:
            data['slug'] = str(newnotify.slug)
        if newnotify.timestamp:
            data['timestamp'] = str(naturaltime(newnotify.timestamp))

        Channel_group(notification_channel(user.id)).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(name='tasks.process_gif')
def process_gif_publication(file, publication_id, user_id=None):
    clip = mp.VideoFileClip(file)
    video_file, media_path = generate_path_video()
    clip.write_videofile(video_file, threads=2)
    PublicationVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('GIF CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        newnotify = Notification.objects.create(actor=user, recipient=user, verb=u'¡tu publicación está lista!',
                                                description='<a href="%s">Ver</a>' % (
                                                    '/publication/' + str(publication_id)))
        data = model_to_dict(newnotify)
        if newnotify.actor:
            data['actor'] = str(newnotify.actor)
        if newnotify.target:
            data['target'] = str(newnotify.target)
        if newnotify.action_object:
            data['action_object'] = str(newnotify.action_object)
        if newnotify.slug:
            data['slug'] = str(newnotify.slug)
        if newnotify.timestamp:
            data['timestamp'] = str(naturaltime(newnotify.timestamp))
        if newnotify.timestamp:
            data['timestamp'] = str(naturaltime(newnotify.timestamp))
        Channel_group(notification_channel(user.id)).send({
            "text": json.dumps(data)
        }, immediately=True)
