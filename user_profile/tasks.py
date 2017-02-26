import json
import publications
from skyfolk.celery import app
from celery.utils.log import get_task_logger
from .models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from publications.utils import get_author_avatar
from django.contrib.humanize.templatetags.humanize import naturaltime
from channels import Group

logger = get_task_logger(__name__)


@app.task()
def send_to_stream(user_id, pub_id):
    profile = None
    publication = None
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        pass
    try:
        publication = publications.models.Publication.objects.get(id=pub_id)
    except ObjectDoesNotExist:
        pass
    if profile:
        logger.info("Sent to followers stream")
        data = {
            'id': publication.id,
            'author_username': publication.author.username,
            'author_first_name': publication.author.first_name,
            'author_last_name': publication.author.last_name,
            'created': naturaltime(publication.created),
            'author_avatar': str(get_author_avatar(authorpk=publication.author)),
            'content': publication.content,
        }
        [Group(follower_channel.news_channel).send({
            "text": json.dumps(data, cls=DjangoJSONEncoder)
        }) for follower_channel in
         profile.get_all_follower_values()]
