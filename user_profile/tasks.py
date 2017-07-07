import json
import publications
from skyfolk.celery import app
from celery.utils.log import get_task_logger
from .models import NodeProfile
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from publications.utils import get_author_avatar
from django.contrib.humanize.templatetags.humanize import naturaltime
from channels import Group
from mailer.mailer import Mailer


logger = get_task_logger(__name__)


@app.task()
def send_to_stream(author_id, pub_id):
    logger.info("AUTHOR: {}".format(author_id))
    author_id = int(author_id)
    try:
        profile = NodeProfile.nodes.get(user_id=author_id)
    except NodeProfile.DoesNotExist:
        raise ValueError("Author not exist")

    try:
        publication = publications.models.Publication.objects.get(id=pub_id)
    except ObjectDoesNotExist:
        raise ValueError("Publication not exist")

    logger.info("Sent to followers stream")

    data = {
        'id': publication.id,
        'author_username': publication.author.username,
        'author_first_name': publication.author.first_name,
        'author_last_name': publication.author.last_name,
        'created': naturaltime(publication.created),
        'author_avatar': str(get_author_avatar(authorpk=publication.author.id)),
        'content': publication.content,
    }
    logger.info("DATA: {}".format(data))
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
