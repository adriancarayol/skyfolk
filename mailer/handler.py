from django.core.exceptions import ObjectDoesNotExist
from user_profile.models import RelationShipProfile
from user_profile.constants import FOLLOWING, BLOCK
from user_profile.tasks import send_email
from django.contrib.auth.models import Group


def notify_via_email(actor, recipients, msg, template, context):
    results = []

    if isinstance(recipients, Group):
        recipients = recipients.user_set.all()

    for recipient in recipients:
        try:
            n = actor.profile
            m = recipient.profile

            if RelationShipProfile.objects.filter(
                    from_profile=n, to_profile=m, type=BLOCK
            ) or RelationShipProfile.objects.filter(
                from_profile=m, to_profile=n, type=BLOCK
            ):
                continue

            if recipient.notification_settings.only_confirmed_users:
                if not actor.is_active:
                    continue

            if not recipient.notification_settings.followed_notifications:
                if RelationShipProfile.objects.filter(
                        from_profile=m, to_profile=n, type=FOLLOWING):
                    continue

            if not recipient.notification_settings.followers_notifications:
                if RelationShipProfile.objects.filter(
                        from_profile=n, to_profile=m, type=FOLLOWING):
                    continue

            results.append(recipient.email)
        except ObjectDoesNotExist:
            continue

    send_email.delay(msg, results, context, template)
