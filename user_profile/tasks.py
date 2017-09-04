import json

from celery.utils.log import get_task_logger
from channels import Group
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string

import publications
from mailer.mailer import Mailer
from skyfolk.celery import app
from .models import NodeProfile

logger = get_task_logger(__name__)


@app.task()
def send_to_stream(author_id, pub_id):
    logger.info("AUTHOR: {}".format(author_id))
    author_id = int(author_id)
    pub_id = int(pub_id)
    #TODO: Error, no encuentra la publicacion?
    try:
        profile = NodeProfile.nodes.get(user_id=author_id)
    except NodeProfile.DoesNotExist:
        raise ValueError("Author not exist")

    try:
        publication = publications.models.Publication.objects.get(id=pub_id)
    except Publication.DoesNotExist:
        raise ValueError("Publication not exist %d" % pub_id)

    logger.info("Sent to followers stream")

    data = {
        'id': publication.id,
        'content': render_to_string(template_name="channels/new_feed_publication.html", context={'item': publication})
    }

    [Group(follower_channel.news_channel).send({
        "text": json.dumps(data, cls=DjangoJSONEncoder)
    }) for follower_channel in
        profile.get_followers()]


@app.task()
def send_email(subject, recipient_list, context, html):
    #TODO: Crear una queue para emails
    """
    Enviar email asincrono al usuario
    """

    mail = Mailer()
    mail.send_messages(subject, template=html, context=context, to_emails=recipient_list)
