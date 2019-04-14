import json
import datetime
import magic
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count, When, Value, Case, IntegerField
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.views.generic import CreateView

from emoji.models import Emoji
from photologue_groups.models import PhotoGroup
from publications.exceptions import (
    MaxFilesReached,
    SizeIncorrect,
    MediaNotSupported,
    CantOpenMedia,
)
from publications.views import logger
from publications_gallery_groups.forms import PublicationPhotoForm, PublicationPhotoEdit
from publications_gallery_groups.models import PublicationGroupMediaPhoto
from user_profile.models import RelationShipProfile, Profile
from user_profile.constants import BLOCK
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from publications_gallery_groups.utils import (
    optimize_publication_media,
    check_num_images,
    check_image_property,
)


class PublicationPhotoView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para una imagen de
    la galeria de un usuario.
    """

    form_class = PublicationPhotoForm
    model = PublicationGroupMediaPhoto
    http_method_names = [u"post"]
    success_url = "/thanks/"

    def __init__(self):
        self.object = None
        super(PublicationPhotoView, self).__init__()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        photo = get_object_or_404(
            PhotoGroup.objects.select_related("group"),
            id=request.POST.get("board_photo", None),
        )

        if not photo.group.is_public and self.request.user.id != photo.group.owner_id:
            if not self.request.user.user_groups.filter(id=photo.group_id).exists():
                return HttpResponseForbidden(
                    "No tienes permiso para publicar en esta imágen"
                )

        emitter = Profile.objects.get(user=self.request.user)
        board_photo_owner = Profile.objects.get(user=photo.owner)

        privacity = board_photo_owner.is_visible(emitter)

        if privacity and privacity != "all":
            raise IntegrityError("No have permissions")

        logger.debug("POST DATA: {}".format(request.POST))
        logger.debug("tipo emitter: {}".format(type(emitter)))

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                parent = publication.parent
                if parent:
                    if RelationShipProfile.objects.is_blocked(
                        to_profile=emitter, from_profile=parent.author.profile
                    ):
                        form.add_error(
                            "board_photo", "El autor de la publicación te ha bloqueado."
                        )
                        return self.form_invalid(form=form)

                publication.author_id = emitter.user_id
                publication.board_photo_id = photo.id

                publication.parse_content()  # parse publication content
                publication.parse_mentions()  # add mentions
                publication.add_hashtag()  # add hashtags

                media = request.FILES.getlist("image")

                try:
                    check_num_images(media)
                except MaxFilesReached:
                    form.add_error(
                        "content", "El número máximo de imágenes que puedes subir es 5."
                    )
                    return self.form_invalid(form=form)

                for file in media:
                    check_image_property(file)

                try:
                    exts = [
                        magic.from_buffer(x.read(), mime=True).split("/") for x in media
                    ]
                except magic.MagicException as e:
                    form.add_error(
                        "content", "No hemos podido procesar los archivos adjuntos."
                    )
                    return self.form_invalid(form=form)

                have_video = False
                if any(
                    word in "gif video"
                    for word in set([item for sublist in exts for item in sublist])
                ):
                    have_video = True

                try:
                    with transaction.atomic(using="default"):
                        publication.save()  # Creamos publicacion
                        form.save_m2m()  # Saving tags
                        transaction.on_commit(
                            lambda: optimize_publication_media(publication, media, exts)
                        )
                        transaction.on_commit(
                            lambda: publication.send_notification(
                                request, is_edited=False
                            )
                        )

                except (SizeIncorrect, MediaNotSupported, CantOpenMedia) as ex:
                    form.add_error("content", str(ex))
                    publication.delete()
                    return self.form_invalid(form=form)

                except Exception as e:
                    raise ValidationError(e)

                if not have_video:
                    return self.form_valid(form=form)
                else:
                    return self.form_valid(
                        form=form,
                        msg=u"Estamos procesando tus videos, te avisamos "
                        u"cuando la publicación esté lista.",
                    )
            except Exception as e:
                form.add_error("content", str(e))
                logger.info("Publication not created -> {}".format(e))

        return self.form_invalid(form=form)


publication_photo_view = login_required(PublicationPhotoView.as_view(), login_url="/")


def publication_detail(request, publication_id):
    """
    Muestra el thread de una conversacion
    """
    user = request.user
    page = request.GET.get("page", 1)
    try:
        request_pub = PublicationGroupMediaPhoto.objects.select_related(
            "board_photo"
        ).get(id=publication_id, deleted=False)

        if (
            not request_pub.board_photo.group.is_public
            and user.id != request_pub.board_photo.group.owner_id
        ):
            if user.user_groups.filter(id=request_pub.board_photo.group_id).exists():
                return redirect(
                    "photologue_groups:photo-list",
                    username=request_pub.board_photo.owner.username,
                )
    except ObjectDoesNotExist:
        raise Http404

    try:
        author = Profile.objects.get(user_id=request_pub.author_id)
        m = Profile.objects.get(user_id=user.id)
    except Profile.DoesNotExist:
        return redirect(
            "photologue_groups:photo-list",
            username=request_pub.board_photo.owner.username,
        )

    privacity = author.is_visible(m)

    if privacity and privacity != "all":
        return redirect(
            "user_profile:profile", username=request_pub.board_photo.owner.username
        )

    try:
        publication = (
            request_pub.get_descendants(include_self=True)
            .annotate(
                likes=Count("user_give_me_like"),
                hates=Count("user_give_me_hate"),
                have_like=Count(
                    Case(
                        When(user_give_me_like=user, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                have_hate=Count(
                    Case(
                        When(user_give_me_hate=user, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
            )
            .filter(deleted=False)
            .prefetch_related(
                "publication_group_multimedia_photo_extra_content",
                "images",
                "videos",
                "tags",
            )
            .select_related("author", "board_photo", "parent")
            .order_by("created")
        )
    except Exception as e:
        raise Exception(
            "No se pudo cargar los descendientes de: {}".format(request_pub)
        )

    paginator = Paginator(publication, 10)

    try:
        publication = paginator.page(page)
    except PageNotAnInteger:
        publication = paginator.page(1)
    except EmptyPage:
        publication = paginator.page(paginator.num_pages)

    context = {
        "publication": publication,
        "publication_id": publication_id,
        "object": request_pub.board_photo,
    }

    return render(request, "photologue_groups/publication_detail.html", context)


@login_required(login_url="/")
@transaction.atomic
def delete_publication(request):
    logger.debug(">>>>>>>> PETICION AJAX BORRAR PUBLICACION")
    response = False
    if request.POST:

        user = request.user
        publication_id = request.POST["publication_id"]
        logger.info(
            "usuario: {} quiere eliminar publicacion: {}".format(
                user.username, publication_id
            )
        )
        # Comprobamos si existe publicacion y que sea de nuestra propiedad
        try:
            publication = PublicationGroupMediaPhoto.objects.select_related(
                "board_photo", "board_photo__group"
            ).get(id=publication_id)
        except PublicationGroupMediaPhoto.DoesNotExist:
            response = False
            return HttpResponse(json.dumps(response), content_type="application/json")
        logger.info(
            "publication_author: {} publication_board_photo: {} request.user: {}".format(
                publication.author.username, publication.board_photo, user.username
            )
        )

        # Borramos publicacion
        if (
            user.id == publication.author.id
            or user.id == publication.board_photo.owner_id
            or user.has_perm("delete_publication", publication.board_video.group)
        ):
            publication.deleted = True
            publication.save(update_fields=["deleted"])
            publication.get_descendants().update(deleted=True)
            if publication.has_extra_content():
                publication.publication_group_multimedia_photo_extra_content.delete()
            logger.info("Publication deleted: {}".format(publication.id))

        response = True
    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required(login_url="/")
@transaction.atomic
def add_like(request):
    response = False
    statuslike = 0
    if request.POST:
        user = request.user
        id_for_publication = request.POST[
            "publication_id"
        ]  # Obtenemos el ID de la publicacion

        try:
            publication = PublicationGroupMediaPhoto.objects.get(
                id=id_for_publication
            )  # Obtenemos la publicacion
        except PublicationGroupMediaPhoto.DoesNotExist:
            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        try:
            author = Profile.objects.get(user_id=publication.author_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        privacity = author.is_visible(m)

        if privacity and privacity != "all":
            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        logger.info("USUARIO DA LIKE")
        logger.info(
            "(USUARIO PETICIÓN): " + user.username + " PK_ID -> " + str(user.pk)
        )
        logger.info(
            "(PERFIL DE USUARIO): "
            + publication.author.username
            + " PK_ID -> "
            + str(publication.author_id)
        )

        in_like = False
        in_hate = False

        if user in publication.user_give_me_like.all():  # Usuario en lista de likes
            in_like = True

        if user in publication.user_give_me_hate.all():  # Usuario en lista de hate
            in_hate = True

        if in_like and in_hate:  # Si esta en ambas listas (situacion no posible)
            publication.user_give_me_like.remove(user)
            publication.user_give_me_hate.remove(user)
            logger.info(
                "Usuario esta en ambas listas, eliminado usuario de ambas listas"
            )

        if in_hate:  # Si ha dado antes unlike
            logger.info("Incrementando like")
            logger.info("Decrementando hate")
            try:
                publication.user_give_me_hate.remove(user)  # remove from hates
                publication.user_give_me_like.add(user)  # add to like
                publication.save()
                response = True
                statuslike = 3

            except IntegrityError:
                response = False
                statuslike = 0

            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        elif in_like:  # Si ha dado antes like
            logger.info("Decrementando like")
            try:
                publication.user_give_me_like.remove(request.user)
                publication.save()
                response = True
                statuslike = 2
            except IntegrityError:
                response = False
                statuslike = 0

            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        else:  # Si no ha dado like ni unlike
            try:
                publication.user_give_me_like.add(user)
                publication.save()
                response = True
                statuslike = 1
            except IntegrityError:
                response = False
                statuslike = 0

    else:
        response = False
        statuslike = 0

    logger.info(
        "Fin like comentario ---> Response"
        + str(response)
        + " Estado"
        + str(statuslike)
    )

    data = json.dumps({"response": response, "statuslike": statuslike})
    return HttpResponse(data, content_type="application/json")


@login_required(login_url="/")
@transaction.atomic
def add_hate(request):
    response = False
    statuslike = 0
    data = []
    if request.POST:
        user = request.user
        id_for_publication = request.POST[
            "publication_id"
        ]  # Obtenemos el ID de la publicacion
        try:
            publication = PublicationGroupMediaPhoto.objects.get(
                id=id_for_publication
            )  # Obtenemos la publicacion
        except PublicationGroupMediaPhoto.DoesNotExist:
            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        try:
            author = Profile.objects.get(user_id=publication.author_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        privacity = author.is_visible(m)

        if privacity and privacity != "all":
            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        logger.info("USUARIO DA HATE")
        logger.info("(USUARIO PETICIÓN): " + user.username)
        logger.info("(PERFIL DE USUARIO): " + publication.author.username)

        in_like = False
        in_hate = False

        if user in publication.user_give_me_like.all():  # Usuario en lista de likes
            in_like = True

        if user in publication.user_give_me_hate.all():  # Usuario en lista de hate
            in_hate = True

        if in_like and in_hate:  # Si esta en ambas listas (situacion no posible)
            publication.user_give_me_like.remove(user)
            publication.user_give_me_hate.remove(user)
            logger.info(
                "Usuario esta en ambas listas, eliminado usuario de ambas listas"
            )

        if in_like:  # Si ha dado antes like
            logger.info("Incrementando hate")
            logger.info("Decrementando like")
            try:
                publication.user_give_me_like.remove(user)  # remove from like
                publication.user_give_me_hate.add(user)  # add to hate
                publication.save()
                response = True
                statuslike = 3

            except IntegrityError:
                response = False
                statuslike = 0

            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        elif in_hate:  # Si ha dado antes hate
            logger.info("Decrementando hate")
            try:
                publication.user_give_me_hate.remove(request.user)
                publication.save()
                response = True
                statuslike = 2
            except IntegrityError:
                response = False
                statuslike = 0

            data = json.dumps({"response": response, "statuslike": statuslike})
            return HttpResponse(data, content_type="application/json")

        else:  # Si no ha dado like ni unlike
            try:
                publication.user_give_me_hate.add(user)
                publication.save()
                response = True
                statuslike = 1
            except IntegrityError:
                response = False
                statuslike = 0
    else:
        response = False
        statuslike = 0

    logger.info(
        "Fin hate comentario ---> Response"
        + str(response)
        + " Estado"
        + str(statuslike)
    )
    data = json.dumps({"response": response, "statuslike": statuslike})
    return HttpResponse(data, content_type="application/json")


@transaction.atomic
def edit_publication(request):
    """
    Permite al creador de la publicacion
    editar el contenido de la publicacion
    """
    if request.method == "POST":
        form = PublicationPhotoEdit(request.POST or None)

        if form.is_valid():
            content = form.cleaned_data["content"]
            pk = form.cleaned_data["pk"]
            user = request.user

            publication = get_object_or_404(PublicationGroupMediaPhoto, id=pk)

            if publication.author_id != user.id:
                return JsonResponse(
                    {"data": "No tienes permisos para editar este comentario"}
                )

            if publication.event_type != 1 and publication.event_type != 3:
                return JsonResponse(
                    {"data": "No puedes editar este tipo de comentario"}
                )

            try:
                publication.content = content
                publication.parse_content()  # parse publication content
                publication.add_hashtag()  # add hashtags
                publication.parse_mentions()

                publication.edition_date = datetime.datetime.now()
                publication._edited = True
                with transaction.atomic(using="default"):
                    publication.save()  # Guardamos la publicacion si no hay errores
                    transaction.on_commit(
                        lambda: publication.send_notification(request, is_edited=True)
                    )
                return JsonResponse({"data": True})
            except IntegrityError:
                return JsonResponse({"data": False})
        else:
            return JsonResponse({"data": False})

    return JsonResponse({"data": "No puedes acceder a esta URL."})


@login_required(login_url="/")
def load_more_descendants(request):
    """
    Carga respuestas de un comentario padre (carga comentarios hijos (nivel 1) de un comentario padre (nivel 0))
    o carga comentarios a respuestas (cargar comentarios descendientes (nivel > 1) de un comentario hijo (nivel 1))
    """
    if request.is_ajax():
        user = request.user
        pub_id = request.GET.get("pubid", None)  # publicacion padre
        page = request.GET.get("page", 1)  # Ultima publicacion add

        print("PAGE: {}, PUB_ID: {}".format(page, pub_id))
        try:
            publication = PublicationGroupMediaPhoto.objects.get(id=pub_id)
        except PublicationGroupMediaPhoto.DoesNotExist:
            return Http404

        try:
            board_owner = Profile.objects.get(user_id=publication.board_photo.owner_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            raise Http404

        privacity = board_owner.is_visible(m)

        if privacity and privacity != "all":
            return HttpResponseForbidden()

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=user.profile, type=BLOCK
        ).values("from_profile_id")

        pubs = (
            publication.get_descendants()
            .filter(~Q(author__profile__in=users_not_blocked_me) & Q(deleted=False))
            .order_by("created")
        )

        pubs = (
            pubs.annotate(
                likes=Count("user_give_me_like"),
                hates=Count("user_give_me_hate"),
                have_like=Count(
                    Case(
                        When(user_give_me_like=user, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                have_hate=Count(
                    Case(
                        When(user_give_me_hate=user, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
            )
            .prefetch_related(
                "publication_group_multimedia_photo_extra_content",
                "images",
                "videos",
                "parent__author",
            )
            .select_related("author", "board_photo", "parent")
        )

        paginator = Paginator(pubs, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        context = {
            "pub_id": pub_id,
            "publications": publications,
            "object": publication.board_photo,
        }
        return render(
            request, "photologue_groups/ajax_load_replies.html", context=context
        )
    return HttpResponseForbidden()
