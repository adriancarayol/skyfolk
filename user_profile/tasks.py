from celery.utils.log import get_task_logger
from mailer.mailer import Mailer
from skyfolk.celery import app
from user_profile.models import Profile
from django.db.models import Count, Q

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
    nodes = Profile.objects.filter(user__notification_settings__email_when_recommendations=True).order_by('?')

    for profile in nodes:
        users = Profile.objects.filter(
            ~Q(user=profile.user)
            & Q(tags__in=profile.tags.all())
            & ~Q(privacity="N")
            & Q(user__is_active=True)
        ).annotate(similarity=Count("tags")).order_by("-similarity").select_related('user')

        if not users:
            continue

        mail = Mailer()
        mail.send_messages('Skyfolk - Tenemos recomendaciones para ti.', template='emails/recommendations.html',
                           context={'to_user': profile.user.username, 'object_list': users},
                           to_emails=[profile.user.email])
