import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, NodeProfile
from publications.models import Publication
from django.db import transaction
from django.contrib.auth.signals import user_logged_in, user_logged_out
from neomodel import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Primera vez que se crea el usuario, creamos Perfil y Nodo
        try:
            with transaction.atomic(using='default'):
                with db.transaction:
                    UserProfile.objects.create(user=instance)
                    NodeProfile(user_id=instance.id, title=instance.username).save()
            logger.info("POST_SAVE : Create UserProfile, User : %s" % instance)
        except Exception:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile/NodeProfile para el user : %s" % instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Comprobamos en cada login del usuario
    si el perfil/nodo se ha creado correctamente
    """
    if not created:
        try:
            with transaction.atomic(using='default'):
                with db.transaction:
                    node = NodeProfile.nodes.get_or_none(user_id=instance.id)
                    if not node:
                        NodeProfile(user_id=instance.id, title=instance.username).save()
                    UserProfile.objects.get_or_create(user=instance)
                    logger.info(
                        "POST_SAVE : Usuario: %s ha iniciado sesion correctamente" % instance.username
                    )
        except Exception:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile/NodeProfile para el user : %s" % instance)
            logger.info("POST_SAVE : Saving UserProfile, User : %s" % instance)


# @receiver(post_save, sender=NodeProfile)
# def handle_new_relationship(sender, instance, created, **kwargs):
#
#     Publication.objects.get_or_create(author=instance.from_person.user,
#                                                        board_owner=instance.from_person.user,
#                                                        content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
#                                                            instance.from_person.user.username,
#                                                            instance.from_person.user.username,
#                                                            instance.to_person.user.username,
#                                                            instance.to_person.user.username),
#                                                        event_type=2)
#
#     Publication.objects.get_or_create(author=instance.from_person.user,
#                                                          board_owner=instance.from_person.user,
#                                                          content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
#                                                              instance.from_person.user.username,
#                                                              instance.from_person.user.username,
#                                                              instance.to_person.user.username,
#                                                              instance.to_person.user.username),
#                                                          event_type=2)
#
#     # Solo conectamos dos usuarios con la relacion "seguidor de"
#     try:
#         from_person = NodeProfile.nodes.get(user_id=instance.from_person.user.id)
#         to_person = NodeProfile.nodes.get(user_id=instance.to_person.user.id)
#         from_person.follow.connect(to_person)
#         logger.info("Nodo creado entre: %s y %s en la graph database" % (
#             instance.from_person.user.username, instance.to_person.user.username))
#
#     except Exception:
#         logger.info("No se pudo crear la union entre: %s y %s en la graph database" % (
#             instance.from_person.user.username, instance.to_person.user.username))
#
#     logger.info(
#     "POST_SAVE : New relationship, user1: {} - user2: {}".format(instance.from_person.user.username,
#                                                                      instance.to_person.user.username))

# @receiver(post_delete, sender=NodeProfile)
# def handle_deleted_relationship(sender, instance, **kwargs):
#     """
#      Eliminar relacion entre dos nodos despues de eliminar una relacion entre usuarios
#     """
#     logger.info("POST_DELETE: Deleted relationshet: user1: {} - user2: {}".format(instance.from_person.user.username,
#                                                                                   instance.to_person.user.username))
#     if instance.status == 1:
#         try:
#             with transaction.atomic(using='default'):
#                 with db.transaction:
#                     from_person = NodeProfile.nodes.get(user_id=instance.from_person.user.id)
#                     to_person = NodeProfile.nodes.get(user_id=instance.to_person.user.id)
#                     from_person.follow.disconnect(to_person)
#                     Publication.objects.filter(author=instance.to_person.user,
#                                                       board_owner=instance.to_person.user,
#                                                       content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
#                                                           instance.to_person.user.username,
#                                                           instance.to_person.user.username,
#                                                           instance.from_person.user.username,
#                                                           instance.from_person.user.username),
#                                                       event_type=2).delete()
#                     Publication.objects.filter(author=instance.from_person.user,
#                                                       board_owner=instance.from_person.user,
#                                                       content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
#                                                           instance.from_person.user.username,
#                                                           instance.from_person.user.username,
#                                                           instance.to_person.user.username,
#                                                           instance.to_person.user.username),
#                                                       event_type=2).delete()
#         except Exception:
#             logger.info("No se pudo eliminar la relacion entre: %s y %s" % (
#                 instance.from_person.user.username, instance.to_person.user.username
#             ))


def handle_login(sender, user, request, **kwargs):
    try:
        user_node = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        NodeProfile(user_id=user.id, title=user.username).save()
    logger.info('User {} is_online'.format(user.username))


def handle_logout(sender, user, request, **kwargs):
    logger.info('User {} is_offlne'.format(user.username))

user_logged_in.connect(handle_login)
user_logged_out.connect(handle_logout)
