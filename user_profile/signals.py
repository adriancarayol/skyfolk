import logging

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from dash.models import DashboardSettings
from .models import (
    Profile,
    RelationShipProfile,
    NotificationSettings,
    LikeProfile,
    FOLLOWING,
)
from notifications.signals import notify
from user_guide.models import Guide, GuideInfo
from badgify.models import Award, Badge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=RelationShipProfile)
def handle_new_relationship(sender, instance, *args, **kwargs):
    type_of_relationship = instance.type

    if type_of_relationship == FOLLOWING:
        instance.weight = instance.weight + 5


def create_user_guides(user):
    guides = Guide.objects.all()
    GuideInfo.objects.bulk_create(
        [GuideInfo(guide=guide, user=user) for guide in guides]
    )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    accept_policy = True
    if created:  # Creatte Profile Notifications settings for User.
        try:
            with transaction.atomic(using="default"):
                Profile.objects.create(user=instance, accepted_policy=accept_policy)
                NotificationSettings.objects.create(user=instance)
                DashboardSettings.objects.create(
                    user=instance, title="Profile", layout_uid="profile", is_public=True
                )
                create_user_guides(instance)
            logger.info("POST_SAVE : Create UserProfile, User : %s" % instance)
        except Exception as e:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile/Notifications/GuideInfo para el user : %s - ERROR: %s"
                % (instance, e)
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Comprobamos en cada login del usuario
    si el perfil/nodo se ha creado correctamente
    """
    if not created:
        try:
            with transaction.atomic(using="default"):
                Profile.objects.get_or_create(user=instance)
                NotificationSettings.objects.get_or_create(user=instance)
                DashboardSettings.objects.get_or_create(
                    user=instance, title="Profile", layout_uid="profile", is_public=True
                )
                logger.info(
                    "POST_SAVE : Usuario: %s ha iniciado sesion correctamente"
                    % instance.username
                )
        except Exception as e:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile para el user : %s"
                % instance
            )
            logger.info("POST_SAVE : Saving UserProfile, User : %s" % instance)

    # Saving profile instance
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass


@receiver(post_save, sender=LikeProfile)
def handle_new_like(sender, instance, created, **kwargs):
    try:
        relation = RelationShipProfile.objects.get(
            from_profile=instance.from_profile,
            to_profile=instance.to_profile,
            type=FOLLOWING,
        )
        relation.weight = relation.weight + 1
    except RelationShipProfile.DoesNotExist:
        pass

    total_likes = LikeProfile.objects.filter(to_profile=instance.to_profile).count()

    if total_likes >= 100:
        Award.objects.get_or_create(
            user=instance.to_profile.user,
            badge=Badge.objects.get(slug="casanova-recipe"),
        )
    elif total_likes >= 5000:
        Award.objects.get_or_create(
            user=instance.to_profile.user,
            badge=Badge.objects.get(slug="don-juan-recipe"),
        )
    elif total_likes >= 150000:
        Award.objects.get_or_create(
            user=instance.to_profile.user,
            badge=Badge.objects.get(slug="influencer-recipe"),
        )

    notify.send(
        instance.from_profile.user,
        actor=instance.from_profile.user.username,
        recipient=instance.to_profile.user,
        description="<a href='/profile/{0}/'>@{0}</a> ha dado me gusta a tu perfil.".format(
            instance.from_profile.user.username
        ),
        verb=u"Nuevo me gusta",
        level="like_profile",
    )


@receiver(post_delete, sender=LikeProfile)
def handle_delete_like(sender, instance, *args, **kwargs):
    try:
        relation = RelationShipProfile.objects.get(
            from_profile=instance.from_profile,
            to_profile=instance.to_profile,
            type=FOLLOWING,
        )
        relation.weight = relation.weight - 1
    except RelationShipProfile.DoesNotExist:
        pass


def handle_login(sender, user, request, **kwargs):
    NotificationSettings.objects.get_or_create(user=user)
    logger.info("User {} is_online".format(user.username))


def handle_logout(sender, user, request, **kwargs):
    cache.delete("seen_%s" % user.username)
    logger.info("User {} is_offlne".format(user.username))


user_logged_in.connect(handle_login)
user_logged_out.connect(handle_logout)
