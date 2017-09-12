from celery.utils.log import get_task_logger
from mailer.mailer import Mailer
from skyfolk.celery import app

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def send_email(subject, recipient_list, context, html):
    # TODO: Crear una queue para emails
    """
    Enviar email asincrono al usuario
    """

    mail = Mailer()
    mail.send_messages(subject, template=html, context=context, to_emails=recipient_list)
