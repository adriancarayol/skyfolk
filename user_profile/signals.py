import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Relationship
from publications.models import Publication
from datetime import datetime
from django.contrib.auth.signals import user_logged_in, user_logged_out

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        logger.info("POST_SAVE : Create UserProfile, User : %s" % instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    logger.info("POST_SAVE : Saving UserProfile, User : %s" % instance)


@receiver(post_save, sender=Relationship)
def handle_new_relationship(sender, instance, created, **kwargs):
    if instance.status == 2:
        e, created = Publication.objects.get_or_create(author=instance.from_person.user,
                                                       board_owner=instance.from_person.user,
                                                       content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
                                                           instance.from_person.user.username,
                                                           instance.from_person.user.username,
                                                           instance.to_person.user.username,
                                                           instance.to_person.user.username),
                                                       event_type=2)
        if not created:
            e.created = datetime.now()
            e.save(update_fields=["created"])
    if instance.status == 1:
        e2, created2 = Publication.objects.get_or_create(author=instance.from_person.user,
                                                         board_owner=instance.from_person.user,
                                                         content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
                                                             instance.from_person.user.username,
                                                             instance.from_person.user.username,
                                                             instance.to_person.user.username,
                                                             instance.to_person.user.username),
                                                         event_type=2)
        if not created2:
            e2.created = datetime.now()
            e2.save(update_fields=["created"])

    logger.info(
        "POST_SAVE : New relationship, user1: {} - user2: {}".format(instance.from_person.user.username,
                                                                     instance.to_person.user.username))


def handle_login(sender, user, request, **kwargs):
    try:
        profile = UserProfile.objects.get(user=user)
        profile.is_online = True
        profile.save(update_fields=['is_online'])
    except Exception:
        pass
    logger.info('login, is_online: {}'.format(user.profile.is_online))


def handle_logout(sender, user, request, **kwargs):
    try:
        profile = UserProfile.objects.get(user=user)
        profile.is_online = False
        profile.save(update_fields=['is_online'])
    except Exception:
        pass
    logger.info('logout, is_online: {}'.format(user.profile.is_online))


user_logged_in.connect(handle_login)
user_logged_out.connect(handle_logout)
