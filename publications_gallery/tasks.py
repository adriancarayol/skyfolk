import json
import os
import publications_gallery

import moviepy.editor as mp
from celery.utils.log import get_task_logger
from channels import Group as Channel_group
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.forms import model_to_dict
from notifications.models import Notification
from skyfolk.celery import app
from user_profile.utils import notification_channel, group_name
from .models import PublicationPhotoVideo, PublicationPhoto
from publications.utils import convert_avi_to_mp4
from django.core.exceptions import ObjectDoesNotExist


logger = get_task_logger(__name__)

@app.task(name='tasks.process_photo_pub_video')
def process_video_publication(file, publication_id, filename, user_id=None):

    try:
        publication = PublicationPhoto.objects.get(id=publication_id)
        photo = publication.board_photo
    except ObjectDoesNotExist:
        return

    video_file, media_path = publications_gallery.utils.generate_path_video()
    if not os.path.exists(os.path.dirname(video_file)):
        os.makedirs(os.path.dirname(video_file))
    convert_avi_to_mp4(file, video_file)
    PublicationPhotoVideo.objects.create(publication_id=publication_id, video=media_path)
    os.remove(file)
    logger.info('VIDEO CONVERTED')
    if user_id:
        user = User.objects.get(id=user_id)
        newnotify = Notification.objects.create(actor=user, recipient=user,
                                                verb=u'¡Ya esta tu video %s!' % filename,
                                                description='<a href="%s">Ver</a>' % (
                                                    '/publication_pdetail/' + str(publication_id)))
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

        data.clear()
        data = {
            'type': "video",
            'video': media_path,
            'id': publication_id
        }
        Channel_group(photo.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)


@app.task(name='tasks.process_photo_pub_gif')
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
        newnotify = Notification.objects.create(actor=user, recipient=user,
                                                verb=u'¡Ya esta tu video %s!' % filename,
                                                description='<a href="%s">Ver</a>' % (
                                                    '/publication_pdetail/' + str(publication_id)))
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

        data.clear()
        data = {
            'type': "video",
            'video': media_path,
            'id': publication_id
        }
        Channel_group(photo.group_name).send({
            "text": json.dumps(data)
        }, immediately=True)
