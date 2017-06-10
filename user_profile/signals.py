import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, NodeProfile, FollowRel
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
                    NodeProfile(user_id=instance.id, title=instance.username,
                                first_name=instance.first_name, last_name=instance.last_name).save()
            logger.info("POST_SAVE : Create UserProfile, User : %s" % instance)
        except Exception as e:
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
                        NodeProfile(user_id=instance.id, title=instance.username,
                                    first_name=instance.first_name, last_name=instance.last_name).save()
                    UserProfile.objects.get_or_create(user=instance)
                    logger.info(
                        "POST_SAVE : Usuario: %s ha iniciado sesion correctamente" % instance.username
                    )
        except Exception as e:
            logger.info(
                "POST_SAVE : No se pudo crear la instancia UserProfile/NodeProfile para el user : %s" % instance)
            logger.info("POST_SAVE : Saving UserProfile, User : %s" % instance)

@receiver(post_save, sender=FollowRel)
def handle_new_relationship(sender, instance, created, **kwargs):
    logging.info("Relationship with weight: {} between: {} - {}".format(instance.weight, instance.start_node().title, instance.end_node().title))

    try:
        with transaction.atomic(using="default"):
            Publication.objects.create(author_id=instance.end_node().user_id,
                                              board_owner_id=instance.end_node().user_id,
                                              content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
                                                  instance.end_node().title,
                                                  instance.end_node().title,
                                                  instance.start_node().title,
                                                  instance.start_node().title),
                                              event_type=2)

            Publication.objects.create(author_id=instance.start_node().user_id,
                                              board_owner_id=instance.start_node().user_id,
                                              content='<i class="fa fa-user-plus" aria-hidden="true"></i> ¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
                                                  instance.start_node().title,
                                                  instance.start_node().title,
                                                  instance.end_node().title,
                                                  instance.end_node().title),
                                              event_type=2)
    except Exception as e:
        logging.info("Publication new relationship can't created")

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


def handle_del(sender, instance, **kwargs):
    print("RELAAAAAAAAAAAAAAAAAATED DELEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEETED")

post_delete.connect(handle_del, sender=FollowRel)