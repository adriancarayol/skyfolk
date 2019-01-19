from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from mailer.mailer import Mailer
from skyfolk.celery import app
from neomodel import db

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def send_email(subject, recipient_list, context, html):
    # TODO: Crear una queue para emails
    """
    Enviar email asincrono al usuario
    """

    mail = Mailer()
    mail.send_messages(subject, template=html, context=context, to_emails=recipient_list)


@app.task(name='tasks.send_recommendation_via_email')
def send_recommendation_via_email():
    """
    Envia recomendaciones de usuarios a los usuarios
    registrados en la web
    """
    nodes = User.objects.filter(notification_settings__email_when_recommendations=True).order_by('?')[:1000]
    
    for user in nodes:
        results, meta = db.cypher_query(
            "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile)<-[:INTEREST]-(u2:NodeProfile) WHERE NOT (u1:NodeProfile)-[:FOLLOW]->(u2:NodeProfile) AND NOT (u2:NodeProfile)-[:BLOCK]->(u1:NodeProfile) AND NOT (u1:NodeProfile)-[:BLOCK]->(u2:NodeProfile) AND u1.title='%s' AND NOT u2.privacity='N' RETURN u2, COUNT(tag) AS score ORDER BY score DESC LIMIT %d" %
            (user.username, 25))

        users = [NodeProfile.inflate(row[0]) for row in results]

        if not users:
            continue

        mail = Mailer()
        mail.send_messages('Skyfolk - Tenemos recomendaciones para ti.', template='emails/recommendations.html',
                           context={'to_user': user.username, 'object_list': users}, to_emails=[user.email])
