import json

from django.contrib.auth.models import User

from publications.models import Publication
from channels import Group
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from user_profile.models import Profile, RelationShipProfile
from celery.utils.log import get_task_logger
from skyfolk.celery import app

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def send_to_stream(author_id, pub_id):
    logger.info("AUTHOR: {}".format(author_id))
    author_id = int(author_id)
    pub_id = int(pub_id)

    try:
        user = User.objects.get(id=author_id)
    except User.DoestNotExist:
        raise Exception("Author not exist")

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        raise ValueError("Author not exist")

    try:
        publication = Publication.objects.get(id=pub_id)
    except Publication.DoesNotExist:
        raise ValueError("Publication not exist %d" % pub_id)

    logger.info("Sent to followers stream")
    logger.info(publication)

    data = {
        'id': publication.id,
        'content': render_to_string(template_name="channels/new_feed_publication.html", context={'item': publication})
    }

    for follower_channel in RelationShipProfile.objects.filter(to_profile=profile):
        Group(follower_channel.from_profile.news_channel).send({
            "text": json.dumps(data, cls=DjangoJSONEncoder)
        })
