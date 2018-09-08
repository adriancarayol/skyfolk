from django.core.exceptions import ObjectDoesNotExist

from user_profile.node_models import NodeProfile
from user_profile.tasks import send_email
from django.contrib.auth.models import Group


def notify_via_email(actor, recipients, msg, template, context):
    results = []

    if isinstance(recipients, Group):
        recipients = recipients.user_set.all()

    for recipient in recipients:
        try:
            try:
                n = NodeProfile.nodes.get(title=actor.username)
                m = NodeProfile.nodes.get(title=recipient.username)
            except NodeProfile.DoesNotExist:
                continue

            if n.bloq.is_connected(m) or m.bloq.is_connected(n):
                continue

            if recipient.notification_settings.only_confirmed_users:
                if not actor.is_active:
                    continue

            if not recipient.notification_settings.followed_notifications:
                if not m.follow.is_connected(n):
                    continue

            if not recipient.notification_settings.followers_notifications:
                if not n.follow.is_connected(m):
                    continue

            results.append(recipient.email)
        except ObjectDoesNotExist:
            continue

    send_email.delay(msg, results,
                     context,
                     template)
