import logging

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from neomodel import db
from dash.models import DashboardWorkspace
from publications.models import Publication
from .models import Profile, RelationShipProfile, NotificationSettings, BLOCK, \
    LikeProfile
from user_profile.node_models import NodeProfile
from notifications.signals import notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=RelationShipProfile)
def handle_new_relationship(sender, instance, created, **kwargs):
    emitter = instance.from_profile.user
    recipient = instance.to_profile.user
    type_of_relationship = instance.type

    try:
        n = NodeProfile.nodes.get(user_id=emitter.id)
        m = NodeProfile.nodes.get(user_id=recipient.id)
    except NodeProfile.DoesNotExist:
        raise Exception("No se encuentran los nodos en neo4j")

    if type_of_relationship == BLOCK:
        n.bloq.connect(m)
    else:
        n.follow.connect(m)
        if created:
            try:
                Publication.objects.update_or_create(author_id=recipient.id,
                                                     board_owner_id=recipient.id,
                                                     content='<i class="material-icons blue1e88e5 left">person_add</i> '
                                                             '¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, '
                                                             '<a href="/profile/%s">@%s</a>!' % (
                                                                 recipient.username,
                                                                 recipient.username,
                                                                 emitter.username,
                                                                 emitter.username),
                                                     event_type=2)

                Publication.objects.update_or_create(author_id=emitter.id,
                                                     board_owner_id=emitter.id,
                                                     content='<i class="material-icons blue1e88e5 left">person_add</i> '
                                                             '¡<a href="/profile/%s">%s</a> ahora sigue a <a '
                                                             'href="/profile/%s">@%s</a>!' % (
                                                                 emitter.username,
                                                                 emitter.username,
                                                                 recipient.username,
                                                                 recipient.username),
                                                     event_type=2)
            except Exception as e:
                raise Exception("Publication relationship not created: {}".format(e))

            # Aumentamos la fuerza de la relacion entre los usuarios
            if n.user_id != m.user_id:
                rel = n.follow.relationship(m)
                if rel:
                    rel.weight = rel.weight + 20
                    rel.save()


@receiver(post_delete, sender=RelationShipProfile)
def handle_delete_relationship(sender, instance, *args, **kwargs):
    emitter_id = instance.from_profile.user_id
    recipient_id = instance.to_profile.user_id

    type_of_relationship = instance.type

    try:
        n = NodeProfile.nodes.get(user_id=emitter_id)
        m = NodeProfile.nodes.get(user_id=recipient_id)
    except NodeProfile.DoesNotExist:
        raise Exception("No se encuentran los nodos en neo4j")

    if type_of_relationship == BLOCK:
        n.bloq.disconnect(m)
    else:
        n.follow.disconnect(m)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Primera vez que se crea el usuario, creamos Perfil y Nodo
        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    Profile.objects.create(user=instance)
                    NotificationSettings.objects.create(user=instance)
                    NodeProfile(user_id=instance.id, title=instance.username,
                                first_name=instance.first_name, last_name=instance.last_name).save()
            logger.info("POST_SAVE : Create UserProfile, User : %s" % instance)
        except Exception as e:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile/NodeProfile para el user : %s" % instance)
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Comprobamos en cada login del usuario
    si el perfil/nodo se ha creado correctamente
    """
    if not created:
        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    node = NodeProfile.nodes.get_or_none(user_id=instance.id)
                    if not node:
                        Profile.objects.get_or_create(user=instance)
                        NotificationSettings.objects.get_or_create(user=instance)
                        DashboardWorkspace.objects.get_or_create(user=instance, position=1, layout_uid="profile",
                                                                 is_public=True,
                                                                 is_clonable=False)
                        NodeProfile(user_id=instance.id, title=instance.username,
                                    first_name=instance.first_name, last_name=instance.last_name).save()
                    logger.info(
                        "POST_SAVE : Usuario: %s ha iniciado sesion correctamente" % instance.username
                    )
        except Exception as e:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile/NodeProfile para el user : %s" % instance)
            logger.info("POST_SAVE : Saving UserProfile, User : %s" % instance)
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)


@receiver(post_save, sender=LikeProfile)
def handle_new_like(sender, instance, created, **kwargs):
    n = NodeProfile.nodes.get(user_id=instance.from_profile.user_id)
    m = NodeProfile.nodes.get(user_id=instance.to_profile.user_id)

    n.like.connect(m)
    rel = n.follow.relationship(m)
    if rel:
        rel.weight = rel.weight + 10
        rel.save()

    notify.send(instance.from_profile.user, actor=instance.from_profile.user.username,
                recipient=instance.to_profile.user,
                description="@{0} ha dado like a tu perfil.".format(instance.from_profile.user.username),
                verb=u'¡<a href="/profile/%s">@%s</a> te ha dado me gusta a tu perfil!.' % (
                    instance.from_profile.user.username, instance.from_profile.user.username), level='like_profile')


@receiver(post_delete, sender=LikeProfile)
def handle_delete_like(sender, instance, *args, **kwargs):
    n = NodeProfile.nodes.get(user_id=instance.from_profile.user_id)
    m = NodeProfile.nodes.get(user_id=instance.to_profile.user_id)

    n.like.disconnect(m)
    rel = n.follow.relationship(m)
    if rel:
        rel.weight = rel.weight - 10
        rel.save()


def handle_login(sender, user, request, **kwargs):
    try:
        user_node = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        NodeProfile(user_id=user.id, title=user.username).save()

    profile = Profile.objects.get_or_create(user_id=user.id)
    NotificationSettings.objects.get_or_create(user=user)
    logger.info('User {} is_online'.format(user.username))


def handle_logout(sender, user, request, **kwargs):
    cache.delete('seen_%s' % user.username)
    logger.info('User {} is_offlne'.format(user.username))


user_logged_in.connect(handle_login)
user_logged_out.connect(handle_logout)
