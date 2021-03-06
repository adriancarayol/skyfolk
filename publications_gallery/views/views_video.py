import json
import datetime
import magic
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count, When, Value, Case, IntegerField, OuterRef, Subquery
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView

from emoji.models import Emoji
from notifications.models import Notification
from photologue.models import Video
from publications.exceptions import (
    MaxFilesReached,
    SizeIncorrect,
    MediaNotSupported,
    CantOpenMedia,
)
from publications.views import logger
from publications_gallery.forms import PublicationVideoForm, PublicationVideoEdit
from publications.forms import SharedPublicationForm
from publications_gallery.models import PublicationVideo
from user_profile.models import RelationShipProfile, Profile
from user_profile.constants import BLOCK
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from publications_gallery.media_processor import (
    optimize_publication_media,
    check_num_images,
    check_image_property,
)


class PublicationVideoView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para un video de
    la galeria de un usuario.
    """

    form_class = PublicationVideoForm
    model = PublicationVideo
    http_method_names = [u"post"]
    success_url = "/thanks/"

    def __init__(self):
        self.object = None
        super(PublicationVideoView, self).__init__()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        video = get_object_or_404(Video, id=request.POST.get("board_video", None))

        emitter = Profile.objects.get(user=self.request.user)
        board_video_owner = Profile.objects.get(user=video.owner)

        privacity = board_video_owner.is_visible(emitter)

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
                            "board_video", "El autor de la publicación te ha bloqueado."
                        )
                        return self.form_invalid(form=form)

                publication.author_id = emitter.user_id
                publication.board_video_id = video.id

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
                print(e)
                form.add_error("content", str(e))
                logger.info("Publication not created -> {}".format(e))

        return self.form_invalid(form=form)


publication_video_view = login_required(PublicationVideoView.as_view(), login_url="/")


class PublicationDetail(View):
    @staticmethod
    def _get_publication_and_descendants(request, video, publications, publication_id, page):
        paginator = Paginator(publications, 1)

        try:
            publication = paginator.page(page)
        except PageNotAnInteger:
            publication = paginator.page(1)
        except EmptyPage:
            publication = paginator.page(paginator.num_pages)

        context = {
            "publication": publication,
            "publication_id": publication_id,
            "object": video,
            "publication_shared": SharedPublicationForm(),
        }

        return render(request, "photologue/videos/publication_detail.html", context)

    def get(self, request, publication_id):
        user = request.user
        page = request.GET.get("page", 1)
        try:
            request_pub = PublicationVideo.objects.select_related("board_video").get(
                id=publication_id, deleted=False
            )
            if (
                    not request_pub.board_video.is_public
                    and user.id != request_pub.board_video.owner.id
            ):
                return redirect(
                    "photologue:photo-list", username=request_pub.board_video.owner.username
                )
        except ObjectDoesNotExist:
            raise Http404

        try:
            author = Profile.objects.get(user_id=request_pub.author_id)
        except Profile.DoesNotExist:
            raise Http404

        if not user.is_authenticated and author.privacity != Profile.ALL:
            return HttpResponseRedirect(reverse('account_login'))

        publication = request_pub.get_descendants(include_self=True).annotate(
            likes=Count("user_give_me_like"),
            hates=Count("user_give_me_hate")
        ).filter(deleted=False).prefetch_related(
            "publication_video_extra_content", "images", "videos", "tags"
        ).select_related("author", "board_video", "parent").order_by("created")

        if not user.is_authenticated and author.privacity == Profile.ALL:
            return self._get_publication_and_descendants(request, request_pub.board_video, publication, publication_id,
                                                         page)

        try:
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            raise Http404

        privacity = author.is_visible(m)

        if privacity and privacity != "all":
            return redirect(
                "user_profile:profile", username=request_pub.board_video.owner.username
            )

        publication = publication.annotate(have_like=Count(
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
            ), )

        return self._get_publication_and_descendants(request, request_pub.board_video, publication, publication_id,
                                                     page)


video_publication_detail = PublicationDetail.as_view()


@login_required(login_url="/")
@transaction.atomic
def delete_video_publication(request):
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
            publication = PublicationVideo.objects.get(id=publication_id)
        except PublicationVideo.DoesNotExist:
            response = False
            return HttpResponse(json.dumps(response), content_type="application/json")
        logger.info(
            "publication_author: {} publication_board_video: {} request.user: {}".format(
                publication.author.username, publication.board_video, user.username
            )
        )

        # Borramos publicacion
        if (
                user.id == publication.author.id
                or user.id == publication.board_video.owner_id
        ):
            publication.deleted = True
            publication.save(update_fields=["deleted"])
            publication.get_descendants().update(deleted=True)
            if publication.has_extra_content():
                publication.publication_video_extra_content.delete()
            logger.info("Publication deleted: {}".format(publication.id))

        response = True
    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required(login_url="/")
@transaction.atomic
def add_video_like(request):
    response = False
    statuslike = 0
    if request.POST:
        user = request.user
        id_for_publication = request.POST[
            "publication_id"
        ]  # Obtenemos el ID de la publicacion

        try:
            publication = PublicationVideo.objects.get(
                id=id_for_publication
            )  # Obtenemos la publicacion
        except PublicationVideo.DoesNotExist:
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
def add_video_hate(request):
    response = False
    statuslike = 0
    data = []
    if request.POST:
        user = request.user
        id_for_publication = request.POST[
            "publication_id"
        ]  # Obtenemos el ID de la publicacion
        try:
            publication = PublicationVideo.objects.get(
                id=id_for_publication
            )  # Obtenemos la publicacion
        except PublicationVideo.DoesNotExist:
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
def edit_video_publication(request):
    """
    Permite al creador de la publicacion
    editar el contenido de la publicacion
    """
    if request.method == "POST":
        form = PublicationVideoEdit(request.POST or None)

        if form.is_valid():
            content = form.cleaned_data["content"]
            pk = form.cleaned_data["pk"]
            user = request.user

            publication = get_object_or_404(PublicationVideo, id=pk)

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


def load_more_video_descendants(request):
    """
    Carga respuestas de un comentario padre (carga comentarios hijos (nivel 1) de un comentario padre (nivel 0))
    o carga comentarios a respuestas (cargar comentarios descendientes (nivel > 1) de un comentario hijo (nivel 1))
    """
    def get_descendants(publication_id, publication_list, board_video):
        pgr = Paginator(publication_list, 10)

        try:
            publication_list = pgr.page(page)
        except PageNotAnInteger:
            publication_list = pgr.page(1)
        except EmptyPage:
            publication_list = pgr.page(pgr.num_pages)

        ctx = {
            "pub_id": publication_id,
            "publications": publication_list,
            "object": board_video,
        }

        return render(
            request, "photologue/videos/ajax_load_replies.html", context=ctx
        )

    if request.is_ajax():
        user = request.user
        pub_id = request.GET.get("pubid", None)  # publicacion padre
        page = request.GET.get("page", 1)  # Ultima publicacion add

        try:
            publication = PublicationVideo.objects.get(id=pub_id)
        except PublicationVideo.DoesNotExist:
            return Http404

        try:
            board_owner = Profile.objects.get(user_id=publication.board_video.owner_id)
        except Profile.DoesNotExist:
            raise Http404

        if not user.is_authenticated and board_owner.privacity != Profile.ALL:
            return HttpResponseForbidden()

        pubs = publication.get_descendants().filter(deleted=False).order_by("created").annotate(
            likes=Count("user_give_me_like"),
            hates=Count("user_give_me_hate"),
        ).prefetch_related(
            "publication_video_extra_content", "images", "videos", "parent__author"
        ).select_related("author", "board_video", "parent")

        if not user.is_authenticated and board_owner.privacity == Profile.ALL:
            return get_descendants(pub_id, pubs, publication.board_video)

        try:
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            raise Http404

        privacity = board_owner.is_visible(m)

        if privacity and privacity != "all":
            return HttpResponseForbidden()

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=user.profile, type=BLOCK
        ).values("from_profile_id")

        pubs = pubs.filter(~Q(author__profile__in=users_not_blocked_me))

        pubs = (
            pubs.annotate(
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
        )

        return get_descendants(pub_id, pubs, publication.board_video)

    return HttpResponseForbidden()
