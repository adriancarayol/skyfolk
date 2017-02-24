import json
import publications
from skyfolk.celery import app
from celery.utils.log import get_task_logger
from .models import UserProfile
from django.core.exceptions import ObjectDoesNotExist

from channels import Group

logger = get_task_logger(__name__)


@app.task(name="send_to_stream")
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
        [Group(follower_channel.news_channel).send({
            "text": json.dumps(publication.content)
        }) for follower_channel in
         profile.get_all_follower_values()]
