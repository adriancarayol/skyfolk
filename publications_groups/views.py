import magic
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db import transaction
from django.db.models import (
    Count,
    Q,
    Case,
    When,
    Value,
    IntegerField,
    Subquery,
    OuterRef,
)
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.views.generic.list import ListView

from emoji.models import Emoji
from notifications.models import Notification
from publications.exceptions import (
    MaxFilesReached,
    SizeIncorrect,
    MediaNotSupported,
    CantOpenMedia,
)
from publications.forms import SharedPublicationForm
from publications.models import Publication
from publications.views import logger
from publications_groups.forms import PublicationGroupForm, GroupPublicationEdit
from publications_groups.models import PublicationGroup
from user_groups.models import UserGroups
from user_profile.models import RelationShipProfile, Profile
from user_profile.constants import BLOCK
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .utils import optimize_publication_media, check_num_images, check_image_property


class PublicationGroupView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para una imagen de
    la galeria de un usuario.
    """

    form_class = PublicationGroupForm
    model = PublicationGroup
    http_method_names = [u"post"]
    success_url = "/thanks/"

    def __init__(self):
        self.object = None
        super(PublicationGroupView, self).__init__()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        group = get_object_or_404(UserGroups, id=request.POST.get("board_group", None))
        emitter = request.user

        is_member = group.users.filter(id=emitter.id).exists()
        if group.owner.id != emitter.id:
            if not group.is_public and not is_member:
                return self.form_invalid(form=form)

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author_id = emitter.id
                publication.board_group_id = group.id
                parent = publication.parent

                if parent:
                    if RelationShipProfile.objects.is_blocked(
                        to_profile=emitter.profile, from_profile=parent.author.profile
                    ):
                        raise PermissionDenied(
                            "El autor de la publicación te ha bloqueado"
                        )

                if not parent and group.owner.id != emitter.id and not is_member:
                    form.add_error("content", "No puedes publicar en este grupo.")
                    return self.form_invalid(form=form)

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
        return self.form_invalid(form=form)


publication_group_view = login_required(PublicationGroupView.as_view(), login_url="/")


class DeletePublication(View):
    http_method_names = ["post"]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, **kwargs):
        user = request.user
        pub_id = request.POST.get("id", None)
        board_group_id = request.POST.get("board_group", None)
        response = "error"

        if not pub_id or not board_group_id:
            return JsonResponse({"response": response})

        try:
            group = UserGroups.objects.get(id=board_group_id)
            publication = PublicationGroup.objects.get(
                id=pub_id, board_group_id=board_group_id
            )
        except ObjectDoesNotExist:
            return JsonResponse({"response": response})

        if publication.author_id == user.id or user.has_perm(
            "delete_publication", group
        ):
            try:
                with transaction.atomic(using="default"):
                    publication.deleted = True
                    publication.save(update_fields=["deleted"])
                    publication.get_descendants().update(deleted=True)
            except Exception as e:
                logger.info(e)
                return JsonResponse({"response": response})
            response = True
        return JsonResponse({"response": response})


delete_publication = login_required(DeletePublication.as_view(), login_url="/")


class AddPublicationLike(View):
    """
    Clase para dar me gusta a un comentario
    """

    model = PublicationGroup

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddPublicationLike, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        pub_id = request.POST.get("pk", None)

        if not user.is_authenticated:
            return HttpResponseForbidden()

        if not pub_id:
            raise Http404

        try:
            publication = PublicationGroup.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            author = Profile.objects.get(user_id=publication.author_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return HttpResponseForbidden()

        privacity = author.is_visible(m)

        if privacity and privacity != "all":
            return HttpResponseForbidden()

        in_like = False
        in_hate = False

        if publication.user_give_me_like.filter(
            pk=user.pk
        ).exists():  # Usuario en lista de likes
            in_like = True

        if publication.user_give_me_hate.filter(
            pk=user.pk
        ).exists():  # Usuario en lista de hate
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

        else:  # Si no ha dado like ni unlike
            try:
                publication.user_give_me_like.add(user)
                publication.save()
                response = True
                statuslike = 1
            except IntegrityError:
                response = False
                statuslike = 0

        data = {"response": response, "statuslike": statuslike}
        return JsonResponse(data)


class AddPublicationHate(View):
    """
    Clase para dar me gusta a un comentario
    """

    model = PublicationGroup

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddPublicationHate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        pub_id = request.POST.get("pk", None)

        if not user.is_authenticated:
            return HttpResponseForbidden()

        if not pub_id:
            raise Http404

        try:
            publication = PublicationGroup.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            author = Profile.objects.get(user_id=publication.author_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return HttpResponseForbidden()

        privacity = author.is_visible(m)

        if privacity and privacity != "all":
            return HttpResponseForbidden()

        in_like = False
        in_hate = False

        if publication.user_give_me_like.filter(
            pk=user.pk
        ).exists():  # Usuario en lista de likes
            in_like = True

        if publication.user_give_me_hate.filter(
            pk=user.pk
        ).exists():  # Usuario en lista de hate
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
                status_like = 3

            except IntegrityError as e:
                response = False
                status_like = 0

        elif in_hate:  # Si ha dado antes hate
            logger.info("Decrementando hate")
            try:
                publication.user_give_me_hate.remove(request.user)
                publication.save()
                response = True
                status_like = 2
            except IntegrityError as e:
                response = False
                status_like = 0

        else:  # Si no ha dado like ni unlike
            try:
                publication.user_give_me_hate.add(user)
                publication.save()
                response = True
                status_like = 1
            except IntegrityError as e:
                response = False
                status_like = 0

        data = {"response": response, "statuslike": status_like}
        return JsonResponse(data)


class EditGroupPublication(UpdateView):
    model = PublicationGroup
    form_class = GroupPublicationEdit

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditGroupPublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = self.request.user
        data = {"response": False}

        content = form.cleaned_data["content"]
        pk = form.cleaned_data["pk"]

        try:
            publication = PublicationGroup.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Http404

        if publication.author.id != user.id:
            return HttpResponseForbidden()

        try:
            publication.content = content
            publication.parse_content()
            publication.add_hashtag()
            publication.parse_mentions()
            publication.edition_date = datetime.datetime.now()
            publication._edited = True
            with transaction.atomic(using="default"):
                publication.save(
                    update_fields=["content"]
                )  # Guardamos la publicacion si no hay errores
                transaction.on_commit(
                    lambda: publication.send_notification(self.request, is_edited=True)
                )

            data["response"] = True
        except IntegrityError:
            pass

        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({"response": False})


class PublicationGroupDetail(ListView):
    model = PublicationGroup
    template_name = "groups/publication_detail.html"

    def __init__(self, **kwargs):
        super(PublicationGroupDetail).__init__(**kwargs)
        self.publication = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PublicationGroupDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pub_id = self.kwargs.get("pk", None)
        page = self.request.GET.get("page", 1)
        user = self.request.user

        try:
            self.publication = PublicationGroup.objects.select_related(
                "board_group"
            ).get(id=pub_id, deleted=False)
        except ObjectDoesNotExist:
            raise Http404

        if (
            not self.publication.board_group.is_public
            and not self.publication.board_group.users.filter(id=user.id).exists()
        ):
            return HttpResponseForbidden()

        try:
            Notification.objects.filter(
                action_object_content_type=ContentType.objects.get_for_model(
                    self.publication
                )
            ).update(unread=False)
        except Notification.DoesNotExist:
            pass

        shared_publications = (
            Publication.objects.filter(
                shared_group_publication__id=OuterRef("pk"), deleted=False
            )
            .order_by()
            .values("shared_group_publication__id")
        )

        total_shared_publications = shared_publications.annotate(c=Count("*")).values(
            "c"
        )

        shared_for_me = shared_publications.annotate(
            have_shared=Count(Case(When(author_id=user.id, then=Value(1))))
        ).values("have_shared")

        publications = (
            self.publication.get_descendants(include_self=True)
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
            .annotate(
                total_shared=Subquery(
                    total_shared_publications, output_field=IntegerField()
                )
            )
            .annotate(have_shared=Subquery(shared_for_me, output_field=IntegerField()))
            .filter(deleted=False)
            .prefetch_related("extra_content", "images", "videos", "tags")
            .select_related("author", "board_group", "parent")
            .order_by("created")
        )

        paginator = Paginator(publications, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)
        return publications

    def get_context_data(self, **kwargs):
        context = super(PublicationGroupDetail, self).get_context_data(**kwargs)
        if not self.request.is_ajax():
            context["publication_id"] = self.kwargs.get("pk", None)
            context["share_publication"] = SharedPublicationForm()
        context["group_profile"] = self.publication.board_group
        context["enable_control_pubs_btn"] = self.request.user.has_perm(
            "delete_publication",
            UserGroups.objects.get(id=self.publication.board_group_id),
        )
        return context


class LoadRepliesForPublicationGroup(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadRepliesForPublicationGroup, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return JsonResponse({"error": "error"})

        user = request.user
        pub_id = request.GET.get("pubid", None)
        page = request.GET.get("page", 1)

        try:
            publication = PublicationGroup.objects.select_related("board_group").get(
                id=pub_id
            )
        except ObjectDoesNotExist:
            raise Http404

        try:
            group = UserGroups.objects.get(id=publication.board_group_id)
        except ObjectDoesNotExist:
            raise Http404

        if group.is_public:
            pass
        else:
            if not group.users.filter(id=user.id).exists():
                return HttpResponseForbidden()

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=user.profile, type=BLOCK
        ).values("from_profile_id")

        pubs = (
            publication.get_descendants()
            .filter(~Q(author__profile__in=users_not_blocked_me) & Q(deleted=False))
            .order_by("created")
        )

        shared_publications = (
            Publication.objects.filter(
                shared_group_publication__id=OuterRef("pk"), deleted=False
            )
            .order_by()
            .values("shared_group_publication__id")
        )

        total_shared_publications = shared_publications.annotate(c=Count("*")).values(
            "c"
        )

        shared_for_me = shared_publications.annotate(
            have_shared=Count(Case(When(author_id=user.id, then=Value(1))))
        ).values("have_shared")

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
            .annotate(
                total_shared=Subquery(
                    total_shared_publications, output_field=IntegerField()
                )
            )
            .annotate(have_shared=Subquery(shared_for_me, output_field=IntegerField()))
            .prefetch_related("extra_content", "images", "videos", "tags")
            .select_related("author", "board_group", "parent")
        )

        paginator = Paginator(pubs, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        try:
            page = publications.next_page_number()
        except EmptyPage:
            page = None

        data = {
            "content": render_to_string(
                request=request,
                template_name="groups/ajax_load_group_replies.html",
                context={"publications": publications, "group_profile": group},
            ),
            "page": page,
            "childs": len(publications),
        }

        return JsonResponse(data)


xstr = lambda s: s or ""


class ShareGroupPublication(View):
    def post(self, request, *args, **kwargs):
        form = SharedPublicationForm(request.POST or None)

        if form.is_valid():
            data = {"response": False}
            user = request.user
            pub_id = form.cleaned_data["pk"]
            try:
                pub_to_add = PublicationGroup.objects.get(id=pub_id)
            except ObjectDoesNotExist:
                raise Http404

            try:
                author = Profile.objects.get(user_id=pub_to_add.author_id)
                m = Profile.objects.get(user_id=user.id)
            except Profile.DoesNotExist:
                raise Http404

            privacity = author.is_visible(m)

            if privacity and privacity != "all":
                return HttpResponseForbidden()

            pub = form.save(commit=False)
            pub.parse_content()
            pub.add_hashtag()
            pub.parse_mentions()

            try:
                obj = Publication.objects.get(
                    shared_group_publication=pub_to_add, author=user, board_owner=user
                )
            except Publication.DoesNotExist:
                obj = Publication.objects.create(
                    shared_group_publication=pub_to_add, author=user, board_owner=user
                )

            obj.created = timezone.now()
            obj.event_type = 6
            obj.deleted = False
            obj.content = pub.content

            with transaction.atomic(using="default"):
                obj.save()
                transaction.on_commit(lambda: obj.send_notification(request))

            data["response"] = True

            return JsonResponse(data)


class RemoveSharedGroupPublication(View):
    model = Publication

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RemoveSharedGroupPublication, self).dispatch(
            request, *args, **kwargs
        )

    def post(self, request, *args, **kwargs):
        pk = request.POST.get("pk", None)
        user = request.user
        try:
            Publication.objects.filter(
                shared_group_publication_id=pk, author_id=user.id, deleted=False
            ).update(deleted=True)
        except ObjectDoesNotExist:
            raise Http404
        data = {"response": True}
        return JsonResponse(data)
