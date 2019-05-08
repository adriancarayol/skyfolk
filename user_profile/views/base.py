import json
import random
import uuid
from itertools import chain, zip_longest

import numpy as np
from allauth.account import app_settings
from allauth.account.utils import get_next_redirect_url, complete_signup
from allauth.account.views import (
    PasswordChangeView,
    EmailView,
    RedirectAuthenticatedUserMixin,
    CloseableSignupMixin,
    sensitive_post_parameters_m,
)
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ViewDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction, IntegrityError
from django.db.models import (
    Case,
    When,
    Value,
    IntegerField,
    OuterRef,
    Subquery,
    Count,
    Q,
    Sum,
)
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from elasticsearch.exceptions import RequestError
from formtools.wizard.views import SessionWizardView
from loguru import logger
from taggit.models import TaggedItem

from avatar.templatetags.avatar_tags import avatar, avatar_url
from awards.models import UserRank
from badgify.models import Award
from dash.base import get_layout
from dash.helpers import iterable_to_dict
from dash.models import DashboardEntry
from dash.utils import (
    get_user_plugins,
    get_workspaces,
    get_public_dashboard_url,
    get_dashboard_settings,
)
from notifications.models import Notification
from notifications.signals import notify
from photologue.models import Photo, Video
from publications.forms import PublicationForm, PublicationEdit, SharedPublicationForm
from publications.models import Publication
from user_groups.models import LikeGroup
from user_groups.models import UserGroups
from user_profile.constants import FOLLOWING, BLOCK
from user_profile.decorators import user_can_view_profile_info
from user_profile.factories.card_user import FactorySkyfolkCardIdentifier
from user_profile.forms import EmailForm, UsernameForm
from user_profile.forms import (
    ProfileForm,
    UserForm,
    SearchForm,
    PrivacityForm,
    DeactivateUserForm,
    ThemesForm,
)
from user_profile.models import (
    Request,
    Profile,
    RelationShipProfile,
    NotificationSettings,
    LikeProfile,
)
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from utils.lists import union_without_duplicates
from user_profile.utils import crop_image, make_pagination_html
from user_profile.views.anonymous_users import AnonymousUserProfileView
from user_profile.views.auth_users import AuthenticatedUserProfileView


def profile_view(request, username):
    """
    Vista principal del perfil de usuario.
    :param username:
    :param template: Template por defecto que muestra el perfil
    :param request:
    """
    user = request.user

    user_profile = get_object_or_404(
        User.objects.select_related("profile"), username__iexact=username
    )

    if user.is_authenticated:
        return AuthenticatedUserProfileView.as_view()(request, username=username)
    elif user_profile.profile.is_public:
        # return AnonymousUserProfileView.as_view()(request, username=username)
        return HttpResponseRedirect(reverse('account_login'))
    else:
        return HttpResponseRedirect(reverse('account_login'))


@login_required(login_url="/")
def config_privacity(request):
    user = request.user
    try:
        profile = Profile.objects.get(user_id=user.id)
    except ObjectDoesNotExist:
        raise Http404

    logger.info(">>>>> PETICION CONFIG - User: {}".format(user.username))
    if request.POST:
        privacity_form = PrivacityForm(data=request.POST)
        if privacity_form.is_valid():
            try:
                with transaction.atomic(using="default"):
                    privacity = privacity_form.clean_privacity()
                    profile.privacity = privacity
                    profile.save()
            except Exception:
                logger.info(
                    ">>>> PETICION CONFIG - User: {} - ERROR".format(user.username)
                )
            logger.info(
                ">>>> PETICION CONFIG - User: {} - CAMBIOS GUARDADOS CORRECTAMENTE".format(
                    user.username
                )
            )
        return HttpResponseRedirect("/config/privacity")
    else:
        privacity_form = PrivacityForm(initial={"privacity": profile.privacity})

    props = {"users": [{"username": user.username, "id": user.id}]}

    return render(
        request,
        "account/cf-privacity.html",
        {
            "showPerfilButtons": True,
            "privacity_form": privacity_form,
            "props": props,
            "component": "leaderboard.js",
        },
    )


@login_required(login_url="/")
def config_profile(request):
    user_profile = Profile.objects.select_related("user").get(user=request.user)
    logger.info(">>>>>>>  PETICION CONFIG")
    if request.POST:
        # formulario enviado
        logger.info(">>>>>>>  paso 1" + str(request.FILES))
        user_form = UserForm(data=request.POST, instance=request.user)
        perfil_form = ProfileForm(request.POST, request.FILES or None, request=request)
        if user_form.is_valid() and perfil_form.is_valid():
            # formulario validado correctamente
            try:
                with transaction.atomic(using="default"):
                    data = perfil_form.clean_backImage()
                    if data:
                        user_profile.back_image.delete()
                        file = crop_image(
                            data,
                            "cover-%s-%s.jpge" % (request.user.username, uuid.uuid4()),
                            request,
                        )
                        user_profile.back_image = file
                    user_profile.status = perfil_form.clean_status()
                    user_profile.save()
                    user_form.save()
                    logger.info(">>>>>>  save")
                    data = {
                        "result": True,
                        "state": 200,
                        "message": "Success",
                        "gallery": "/config/profile",
                    }
                    return JsonResponse({"data": data})
            except Exception as e:
                logger.info(
                    "No se pudo guardar la configuracion del perfil de la cuenta: {}".format(
                        request.user.username
                    )
                )
                data = {"result": False, "state": 500, "message": "Success"}

                return JsonResponse({"data": data})
    else:
        # formulario inicial
        user_form = UserForm(instance=request.user)
        perfil_form = ProfileForm(initial={"status": user_profile.status})

    logger.info(">>>>>>>  paso x")
    context = {
        "showPerfilButtons": True,
        "user_profile": user_profile,
        "user_form": user_form,
        "perfil_form": perfil_form,
    }
    return render(request, "account/cf-profile.html", context)
    # return render_to_response('account/cf-profile.html',
    # {'showPerfilButtons':True,'searchForm':searchForm,
    # 'user_form':user_form}, context_instance=RequestContext(request))


@login_required(login_url="/")
def config_blocked(request):
    user = request.user
    list_blocked = RelationShipProfile.objects.filter(
        from_profile__user=user, type=BLOCK
    ).select_related("to_profile__user")

    return render(
        request,
        "account/cf-blocked.html",
        {"showPerfilButtons": True, "blocked": list_blocked},
    )


class InterestsView(FormView):
    template_name = "account/cf-interests.html"
    form_class = ThemesForm
    success_url = "/config/interests/"

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None)

        if not form.is_valid():
            return super().post(request, *args, **kwargs)

        user = request.user
        user_profile = user.profile

        response = "success"

        tags = request.POST.getlist("tags[]")
        choices = request.POST.getlist("choices[]")
        choices = [
            dict(ThemesForm.CHOICES).get(choice, "").lower() for choice in choices
        ]
        interests = union_without_duplicates(tags, choices)

        for tag in interests:
            if tag.isspace():
                response = "with_spaces"
                return HttpResponse(
                    json.dumps(response), content_type="application/json"
                )

            tag = tag.lower()
            interest_exists = user_profile.tags.filter(name__iexact=tag).exists()

            if not interest_exists and tag:
                with transaction.atomic():
                    user_profile.tags.add(tag)

        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_interests"] = self.request.user.profile.tags.all().values_list(
            "name", "id"
        )
        context["form"] = ThemesForm
        return context


class AffinityView(TemplateView):
    template_name = "account/cf-affinity.html"

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        # Get follows and followers of user
        relation_ships = (
            RelationShipProfile.objects.filter(
                Q(from_profile__user=user) | Q(to_profile__user=user)
            )
            .order_by("-weight")
            .select_related("from_profile__user", "to_profile__user")[:1000]
        )

        user_already_exists_in_nodes = []
        edges = []

        nodes = []

        for relation in relation_ships:
            r = lambda: random.randint(0, 255)

            if relation.from_profile.user_id not in user_already_exists_in_nodes:
                user_already_exists_in_nodes.append(relation.from_profile.user_id)
                nodes.append(
                    {
                        "id": "n" + str(relation.from_profile.user_id),
                        "label": str(relation.from_profile.user.username),
                        "x": random.uniform(0, 0.1),
                        "y": random.uniform(0, 0.1),
                        "size": relation.weight,
                        "color": "#%02X%02X%02X" % (r(), r(), r()),
                    }
                )

            if relation.to_profile.user_id not in user_already_exists_in_nodes:
                user_already_exists_in_nodes.append(relation.to_profile.user_id)
                nodes.append(
                    {
                        "id": "n" + str(relation.to_profile.user_id),
                        "label": str(relation.to_profile.user.username),
                        "x": random.uniform(0, 0.1),
                        "y": random.uniform(0, 0.1),
                        "size": relation.weight,
                        "color": "#%02X%02X%02X" % (r(), r(), r()),
                    }
                )

            edges.append(
                {
                    "id": "e" + str(relation.id),
                    "source": "n" + str(relation.from_profile.user_id),
                    "target": "n" + str(relation.to_profile.user_id),
                    "label": str(relation.weight),
                }
            )

        data = {"nodes": nodes, "edges": edges}

        context["data"] = json.dumps(data)
        return context


@login_required(login_url="accounts/login")
def add_friend_by_username_or_pin(request):
    """
    Funcion para añadir usuario por nombre de usuario y perfil
    """
    logger.info("ADD FRIEND BY USERNAME OR PIN")
    response = "no_added_friend"
    friend = None
    data = {"response": response, "friend": friend}
    if request.method == "POST":
        username = str(request.POST.get("valor"))
        if not username:
            return HttpResponse(
                json.dumps(
                    json.dumps({"response": "your_own_pin"}),
                    content_type="application/javascript",
                )
            )
        else:  # tipo == username
            user_request = request.user

            if user_request.username == username:
                data["response"] = "your_own_username"
                return HttpResponse(
                    json.dumps(data), content_type="application/javascript"
                )

            try:
                friend = Profile.objects.get(user__username=username)
                user_profile = Profile.objects.get(user_id=user_request.id)
            except Profile.DoesNotExist:
                data["response"] = "no_match"
                return HttpResponse(
                    json.dumps(data), content_type="application/javascript"
                )

            if RelationShipProfile.objects.is_follow(
                from_profile=user_profile, to_profile=friend
            ):
                data["response"] = "its_your_friend"
                data["friend"] = friend.user.username
                return HttpResponse(
                    json.dumps(data), content_type="application/javascript"
                )

            # Me tienen bloqueado
            if RelationShipProfile.objects.is_blocked(
                from_profile=friend, to_profile=user_profile
            ):
                data["response"] = "user_blocked"
                data["friend"] = friend.user.username
                return HttpResponse(
                    json.dumps(data), content_type="application/javascript"
                )

            # Yo tengo bloqueado al perfil
            if RelationShipProfile.objects.is_blocked(
                from_profile=user_profile, to_profile=friend
            ):
                data["response"] = "blocked_profile"
                data["friend"] = friend.user.username
                return HttpResponse(
                    json.dumps(data), content_type="application/javascript"
                )

            # Comprobamos si el usuario necesita peticion de amistad
            no_need_petition = friend.privacity == Profile.ALL
            if no_need_petition:
                try:
                    RelationShipProfile.objects.create(
                        to_profile=friend, from_profile=user_profile, type=FOLLOWING
                    )
                    data["response"] = "added_friend"
                except Exception as e:
                    logger.info(e)
                    return HttpResponse(
                        json.dumps(data), content_type="application/javascript"
                    )

                data["friend_username"] = friend.user.username
                data["friend_avatar"] = avatar(friend.user)
                data["friend_first_name"] = friend.user.first_name
                data["friend_last_name"] = friend.user.last_name
                return HttpResponse(
                    json.dumps(data), content_type="application/javascript"
                )

            # enviamos peticion de amistad
            try:
                friend_request = Request.objects.get_follow_request(
                    from_profile=user_profile.user_id, to_profile=friend.user_id
                )
                response = "in_progress"
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                Notification.objects.filter(
                    actor_object_id=user_request.pk,
                    recipient=friend.user,
                    level="friendrequest",
                ).delete()
                # Enviamos nueva notificacion
                notification = notify.send(
                    user_request,
                    actor=User.objects.get(pk=user_request.pk).username,
                    recipient=friend.user,
                    description=u'<a href="/profile/{0}/">@{0}</a> quiere seguirte.'.format(
                        user_request.username
                    ),
                    verb=u"Nueva petición de seguimiento",
                    level="friendrequest",
                )
                # Enlazamos notificacion y peticion de amistad
                try:
                    Request.objects.add_follow_request(
                        user_profile.user_id, friend.user_id, notification[0][1]
                    )
                    response = "new_petition"
                except ObjectDoesNotExist:
                    response = "no_added_friend"

    data["response"] = response
    data["friend_username"] = friend.user.username
    data["friend_avatar"] = avatar(friend.user)
    data["friend_first_name"] = friend.user.first_name
    data["friend_last_name"] = friend.user.last_name

    return HttpResponse(json.dumps(data), content_type="application/javascript")


@login_required(login_url="/")
def like_profile(request):
    """
    Funcion para dar like al perfil
    """
    response = "like"
    if request.method == "POST":
        user = request.user
        slug = request.POST.get("slug", None)

        if slug is not None and slug.isnumeric():
            slug = int(slug)

        if slug == user.id:
            return HttpResponseBadRequest()

        try:
            n = Profile.objects.get(user_id=user.id)
            m = Profile.objects.get(user_id=slug)
        except (Profile.DoesNotExist, ValueError) as e:
            raise Http404

        if LikeProfile.objects.filter(to_profile=m, from_profile=n).exists():
            try:
                LikeProfile.objects.filter(to_profile=m, from_profile=n).delete()
                response = "nolike"
            except Exception as e:
                pass
        else:
            try:
                LikeProfile.objects.create(to_profile=m, from_profile=n)
                response = "like"
            except Exception as e:
                pass

        logger.info(
            "Response like_function (to_like: {} from_like: {}) response = {}".format(
                m.user, n.user, response
            )
        )

    return HttpResponse(json.dumps(response), content_type="application/javascript")


# Request follow
@login_required(login_url="accounts/login")
def request_friend(request):
    """
    Funcion para solicitudes de amistad
    """
    logger.info(">>>>>>> peticion amistad ")
    response = "null"
    if request.method == "POST":
        user = request.user
        slug = request.POST.get("slug", None)

        if slug is not None and slug.isnumeric():
            slug = int(slug)

        if slug == user.id:
            return HttpResponseBadRequest()

        try:
            n = Profile.objects.get(user_id=user.id)
            m = Profile.objects.get(user_id=slug)
        except Profile.DoesNotExist:
            return HttpResponse(
                json.dumps(response), content_type="application/javascript"
            )

        # El perfil me ha bloqueado

        if RelationShipProfile.objects.is_blocked(from_profile=m, to_profile=n):
            response = "user_blocked"
            return HttpResponse(
                json.dumps(response), content_type="application/javascript"
            )

        try:
            user_friend = RelationShipProfile.objects.is_follow(
                from_profile=n, to_profile=m
            )  # Comprobamos si YO ya sigo al perfil deseado.
        except Exception:
            user_friend = None

        if user_friend:
            response = "isfriend"
        else:
            # Comprobamos si el perfil necesita peticion de amistad
            no_need_petition = m.privacity == Profile.ALL
            if no_need_petition:
                try:
                    with transaction.atomic(using="default"):
                        RelationShipProfile.objects.create(
                            to_profile=m, from_profile=n, type=FOLLOWING
                        )
                        # enviamos notificacion informando del evento
                        notify.send(
                            user,
                            actor=n.user.username,
                            recipient=m.user,
                            action_object=user,
                            description="<a href='/profile/{0}/'>@{0}</a> ahora es tu seguidor.".format(
                                user.username
                            ),
                            verb=u"Nuevo seguidor",
                            level="new_follow",
                        )
                    response = "added_friend"
                except Exception as e:
                    logger.info(e)
                    response = "no_added_friend"

                return HttpResponse(
                    json.dumps(response), content_type="application/javascript"
                )
            response = "inprogress"

            try:
                friend_request = Request.objects.get_follow_request(
                    from_profile=n.user_id, to_profile=m.user_id
                )
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                Notification.objects.filter(
                    actor_object_id=n.user_id,
                    recipient=m.user_id,
                    level="friendrequest",
                ).delete()

                # Creamos y enviamos la nueva notificacion
                notification = notify.send(
                    user,
                    actor=n.user.username,
                    recipient=m.user,
                    description="@{0} quiere seguirte.".format(n.user.username),
                    verb=u"Nueva solicitud de seguimiento",
                    level="friendrequest",
                )

                # Enlazamos notificacion con peticion de amistad
                try:
                    Request.objects.add_follow_request(
                        n.user_id, m.user_id, notification[0][1]
                    )

                except ObjectDoesNotExist:
                    response = "no_added_friend"

        logger.info(response)

    return HttpResponse(json.dumps(response), content_type="application/javascript")


# Responde request follow
@login_required(login_url="/")
def respond_friend_request(request):
    """
    Funcion para respuesta a solicitud de amistad
    """
    response = "null"
    if request.method == "POST":
        user = request.user
        profile_user_id = request.POST.get("slug", None)
        request_status = request.POST.get("status", None)

        if profile_user_id is not None and profile_user_id.isnumeric():
            profile_user_id = int(profile_user_id)

        if user.id == profile_user_id:
            return HttpResponseBadRequest()

        try:
            recipient = User.objects.select_related("profile").get(id=profile_user_id)
            emitter = Profile.objects.get(user_id=user.id)
        except ObjectDoesNotExist:
            return HttpResponse(
                json.dumps(response), content_type="application/javascript"
            )

        if request_status == "accept":
            try:
                with transaction.atomic(using="default"):
                    RelationShipProfile.objects.create(
                        to_profile=emitter,
                        from_profile=recipient.profile,
                        type=FOLLOWING,
                    )
                    notify.send(
                        user,
                        actor=user.username,
                        recipient=recipient,
                        action_object=user,
                        description="@{0} ha aceptado tu solicitud de seguimiento.".format(
                            user.username
                        ),
                        verb=u"Petición aceptada",
                        level="new_follow",
                    )

                    Request.objects.remove_received_follow_request(
                        from_profile=recipient.id, to_profile=user.id
                    )

                response = "added_friend"
                logger.info(
                    "user.profile: {} emitter_profile: {}".format(
                        user.username, recipient.id
                    )
                )
                # enviamos notificacion informando del evento
            except Exception as e:
                logger.info(e)
                response = "rejected"

        elif request_status == "rejected":
            try:
                with transaction.atomic(using="default"):
                    Request.objects.remove_received_follow_request(
                        from_profile=recipient.id, to_profile=user.id
                    )
                response = "rejected"
            except Exception as e:
                response = "null"
        else:
            response = "rejected"

    return HttpResponse(json.dumps(response), content_type="application/javascript")


# Elimina relación entre dos usuarios
@login_required(login_url="/")
def remove_relationship(request):
    """
    Elimina relacion seguidor/seguido
    """
    response = None
    user = request.user
    slug = request.POST.get("slug", None)

    if slug is not None and slug.isnumeric():
        slug = int(slug)

    if user.id == slug:
        return HttpResponseBadRequest()

    if request.method == "POST":
        try:
            profile_user = Profile.objects.get(user_id=slug)
            me = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return HttpResponse(
                json.dumps(response), content_type="application/javascript"
            )

        if RelationShipProfile.objects.is_follow(
            from_profile=me, to_profile=profile_user
        ):
            try:
                RelationShipProfile.objects.filter(
                    to_profile=profile_user, from_profile=me, type=FOLLOWING
                ).delete()
                response = True
            except Exception as e:
                logger.info(e)
                response = None

    return HttpResponse(json.dumps(response), content_type="application/javascript")


@login_required(login_url="/")
def remove_blocked(request):
    """
    Elimina relacion de bloqueo
    """
    response = None
    user = request.user
    slug = request.POST.get("slug", None)

    if slug is not None and slug.isnumeric():
        slug = int(slug)

    if user.id == slug:
        return HttpResponseBadRequest()

    if request.method == "POST":
        try:
            m = Profile.objects.get(user_id=user.id)
            n = Profile.objects.get(user_id=slug)
        except Profile.DoesNotExist:
            return HttpResponse(
                json.dumps(response), content_type="application/javascript"
            )

        try:
            if RelationShipProfile.objects.filter(
                from_profile=m, to_profile=n, type=BLOCK
            ).exists():
                RelationShipProfile.objects.filter(
                    to_profile=n, from_profile=m, type=BLOCK
                ).delete()
                response = True
            else:
                logger.info("%s no tiene bloqueado a %s" % (m.username, n.username))
                response = False
        except Exception as e:
            logger.info(e)
            response = False

    return HttpResponse(json.dumps(response), content_type="application/javascript")


# Elimina la peticion existente para seguir a un perfil
@login_required(login_url="/")
def remove_request_follow(request):
    """
    Elimina relacion de seguidos
    """
    response = False
    user = request.user
    slug = request.POST.get("slug", None)
    status = request.POST.get("status", None)

    if slug is not None and slug.isnumeric():
        slug = int(slug)

    if user.id == slug:
        return HttpResponseBadRequest()

    logger.info("REMOVE REQUEST FOLLOW: u1: {} - u2: {}".format(user.id, slug))
    if request.method == "POST":
        if status == "cancel":
            try:
                with transaction.atomic(using="default"):
                    response = Request.objects.remove_received_follow_request(
                        from_profile=user.id, to_profile=slug
                    )
            except (ObjectDoesNotExist, IntegrityError) as e:
                response = False
            response = True
        else:
            response = False
        logger.info("Response -> " + str(response))
    return HttpResponse(json.dumps(response), content_type="application/javascript")


class FollowersListView(TemplateView):
    """
    Lista de seguidores del usuario
    """

    template_name = "account/relations.html"

    @method_decorator(user_can_view_profile_info)
    def dispatch(self, request, *args, **kwargs):
        return super(FollowersListView, self).dispatch(request, *args, **kwargs)

    def _get_relation_ships(self):
        username = self.kwargs.get("username", None)
        page = self.request.GET.get("page", 1)

        try:
            profile = Profile.objects.get(user__username=username)
        except ObjectDoesNotExist:
            raise Http404()

        paginator = Paginator(
            RelationShipProfile.objects.filter(
                to_profile=profile, type=FOLLOWING
            ).select_related("from_profile__user"),
            25,
        )

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return users

    def get_followers(self, qs):
        ct = ContentType.objects.get_for_model(Profile)
        ids = [result.from_profile.id for result in qs]

        following_result = []

        videos = (
            Video.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(videos_count=Count("owner__profile__id"))
            .values("owner__profile__id", "videos_count")
            .order_by()
        )
        photos = (
            Photo.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(photos_count=Count("owner__profile__id"))
            .values("owner__profile__id", "photos_count")
            .order_by()
        )
        followers_result = (
            RelationShipProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(follower_count=Count("to_profile_id"))
            .values("follower_count", "to_profile_id")
            .order_by()
        )
        likes = (
            LikeProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(likes_count=Count("to_profile_id"))
            .order_by()
        )
        total_exp = (
            Award.objects.filter(user__profile__id__in=ids)
            .values("user_id")
            .annotate(exp_count=Sum("badge__points"))
            .values("user_id", "exp_count")
            .order_by()
        )
        last_ranks = (
            UserRank.objects.filter(users__id__in=ids)
            .values("users__id")
            .order_by("-reached_with")
            .values("users__id", "name", "description")
        )

        seen = set()
        last_ranks = [
            last_rank
            for last_rank in last_ranks
            if [last_rank["users__id"] not in seen, seen.add(last_rank["users__id"])][0]
        ]

        for follow in qs:
            tagged_items = TaggedItem.objects.filter(
                content_type=ct, object_id=follow.from_profile.id
            ).select_related("tag")[:10]
            result_object = {
                "profile": follow.from_profile,
                "tags": [tag.tag for tag in tagged_items],
                "videos": next(
                    iter(
                        [
                            video["videos_count"]
                            for video in videos
                            if video["owner__profile__id"] == follow.from_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "photos": next(
                    iter(
                        [
                            photo["photos_count"]
                            for photo in photos
                            if photo["owner__profile__id"] == follow.from_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "followers": next(
                    iter(
                        [
                            follower["follower_count"]
                            for follower in followers_result
                            if follower["to_profile_id"] == follow.from_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "likes": next(
                    iter(
                        [
                            like["likes_count"]
                            for like in likes
                            if like["to_profile_id"] == follow.from_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "last_rank": next(
                    iter(
                        [
                            last_rank
                            for last_rank in last_ranks
                            if follow.from_profile.user_id == last_rank["users__id"]
                        ]
                        or []
                    ),
                    {},
                ),
                "exp": next(
                    iter(
                        [
                            exp["exp_count"]
                            for exp in total_exp
                            if exp["user_id"] == follow.from_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
            }
            following_result.append(result_object)

        return following_result

    def get_context_data(self, **kwargs):
        context = super(FollowersListView, self).get_context_data(**kwargs)
        context["url_name"] = "followers"
        relation_ships = self._get_relation_ships()
        context["relation_ships"] = relation_ships
        context["object_list"] = self.get_followers(relation_ships)
        # context["component"] = "followers_react.js"
        context["username"] = self.kwargs.get("username", None)
        return context


followers = login_required(FollowersListView.as_view())


class FollowingListView(TemplateView):
    """
    Lista de seguidos del usuario
    """

    template_name = "account/relations.html"

    @method_decorator(user_can_view_profile_info)
    def dispatch(self, request, *args, **kwargs):
        return super(FollowingListView, self).dispatch(request, *args, **kwargs)

    def _get_relation_ships(self):
        username = self.kwargs.get("username", None)
        page = self.request.GET.get("page", 1)

        try:
            profile = Profile.objects.get(user__username=username)
        except ObjectDoesNotExist:
            raise Http404()

        paginator = Paginator(
            RelationShipProfile.objects.filter(
                from_profile=profile, type=FOLLOWING
            ).select_related("to_profile__user"),
            25,
        )

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return users

    def get_following(self, qs):
        ct = ContentType.objects.get_for_model(Profile)
        ids = [result.to_profile.id for result in qs]

        following_result = []

        videos = (
            Video.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(videos_count=Count("id"))
            .values("owner__profile__id", "videos_count")
            .order_by()
        )
        photos = (
            Photo.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(photos_count=Count("id"))
            .values("owner__profile__id", "photos_count")
            .order_by()
        )
        followers_result = (
            RelationShipProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(follower_count=Count("to_profile"))
            .values("follower_count", "to_profile_id")
            .order_by()
        )
        likes = (
            LikeProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(likes_count=Count("to_profile"))
            .values("to_profile_id", "likes_count")
            .order_by()
        )
        total_exp = (
            Award.objects.filter(user__profile__id__in=ids)
            .values("user_id")
            .annotate(exp_count=Sum("badge__points"))
            .values("user_id", "exp_count")
            .order_by()
        )
        last_ranks = (
            UserRank.objects.filter(users__id__in=ids)
            .values("users__id")
            .order_by("-reached_with")
            .values("users__id", "name", "description")
        )

        seen = set()
        last_ranks = [
            last_rank
            for last_rank in last_ranks
            if [last_rank["users__id"] not in seen, seen.add(last_rank["users__id"])][0]
        ]

        for follow in qs:
            tagged_items = TaggedItem.objects.filter(
                content_type=ct, object_id=follow.to_profile.id
            ).select_related("tag")[:10]
            result_object = {
                "profile": follow.to_profile,
                "tags": [tag.tag for tag in tagged_items],
                "videos": next(
                    iter(
                        [
                            video["videos_count"]
                            for video in videos
                            if video["owner__profile__id"] == follow.to_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "photos": next(
                    iter(
                        [
                            photo["photos_count"]
                            for photo in photos
                            if photo["owner__profile__id"] == follow.to_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "followers": next(
                    iter(
                        [
                            follower["follower_count"]
                            for follower in followers_result
                            if follower["to_profile_id"] == follow.to_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "last_rank": next(
                    iter(
                        [
                            last_rank
                            for last_rank in last_ranks
                            if follow.to_profile.user_id == last_rank["users__id"]
                        ]
                        or []
                    ),
                    {},
                ),
                "likes": next(
                    iter(
                        [
                            like["likes_count"]
                            for like in likes
                            if like["to_profile_id"] == follow.to_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
                "exp": next(
                    iter(
                        [
                            exp["exp_count"]
                            for exp in total_exp
                            if exp["user_id"] == follow.to_profile.id
                        ]
                        or []
                    ),
                    0,
                ),
            }
            following_result.append(result_object)

        return following_result

    def get_context_data(self, **kwargs):
        context = super(FollowingListView, self).get_context_data(**kwargs)
        context["url_name"] = "following"
        relation_ships = self._get_relation_ships()
        context["relation_ships"] = relation_ships
        context["object_list"] = self.get_following(relation_ships)
        # context["component"] = "following_react.js"
        context["username"] = self.kwargs.get("username", None)
        return context


following = login_required(FollowingListView.as_view())


class PassWordChangeDone(TemplateView):
    template_name = "account/confirmation_changepass.html"

    def get(self, request, *args, **kwargs):
        context = locals()
        user = self.request.user
        context["showPerfilButtons"] = True
        return render(request, self.template_name, context)


password_done = login_required(PassWordChangeDone.as_view())


# Modificacion del formulario para cambiar contraseña
class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy("user_profile:account_done_password")

    def get_context_data(self, **kwargs):
        ret = super(PasswordChangeView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret["password_change_form"] = ret.get("form")
        ret["showPerfilButtons"] = True
        # (end NOTE)
        return ret


custom_password_change = login_required(CustomPasswordChangeView.as_view())


# Modificacion del formulario para manejar los emails
class CustomEmailView(EmailView):
    success_url = reverse_lazy("user_profile:account_email")

    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        user = self.request.user
        ret["add_email_form"] = ret.get("form")
        ret["showPerfilButtons"] = True
        # (end NOTE)
        return ret


custom_email = login_required(CustomEmailView.as_view())


@login_required(login_url="/")
def changepass_confirmation(request):
    return render(request, "account/confirmation_changepass.html")


# Modificacion del template para desactivar una cuenta
class DeactivateAccount(FormView):
    template_name = "account/cf-account_inactive.html"
    form_class = DeactivateUserForm
    success_url = reverse_lazy("account_logout")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["form"] = self.form_class
        user = self.request.user
        self_initial = {"author": user.pk, "board_owner": user.pk}

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        user = request.user
        if user.is_authenticated:
            if form.is_valid():
                try:
                    with transaction.atomic(using="default"):
                        is_active = not (form.clean_is_active())
                        user.is_active = is_active
                        user.save()
                except Exception as e:
                    logger.info(
                        "La cuenta de: {} no se pudo desactivar".format(user.username)
                    )

                if user.is_active:
                    return self.form_valid(form=form, **kwargs)
                else:
                    return HttpResponseRedirect(self.success_url)
            else:
                return self.form_invalid(form=form, **kwargs)
        else:
            raise PermissionError

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context)


custom_delete_account = login_required(DeactivateAccount.as_view())


@login_required(login_url="/")
def bloq_user(request):
    """
        Funcion para bloquear usuarios
    """
    user = request.user
    haslike = "noliked"
    status = "none"

    if request.method == "POST":
        id_user = request.POST.get("id_user", None)

        if id_user is not None and id_user.isnumeric():
            id_user = int(id_user)

        if id_user == user.id:
            data = {"response": False, "haslike": haslike}
            return HttpResponse(json.dumps(data), content_type="application/json")

        try:
            n = Profile.objects.get(user_id=id_user)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            data = {"response": False, "haslike": haslike}
            return HttpResponse(json.dumps(data), content_type="application/json")

        # Eliminar me gusta al perfil que se va a bloquear
        deleted = LikeProfile.objects.filter(from_profile=m, to_profile=n).delete()
        if deleted:
            haslike = "liked"

        # Ver si hay una peticion de "seguir" pendiente
        try:
            follow_request = Request.objects.get_follow_request(
                from_profile=m.user_id, to_profile=n.user_id
            )
        except ObjectDoesNotExist:
            follow_request = None

        if follow_request:
            Request.objects.remove_received_follow_request(
                from_profile=m.user_id, to_profile=n.user_id
            )
            status = "inprogress"

        # Ver si seguimos al perfil que vamos a bloquear
        emitter = Profile.objects.get(user_id=user.id)
        recipient = Profile.objects.get(user_id=id_user)

        if RelationShipProfile.objects.is_follow(
            from_profile=emitter, to_profile=recipient
        ):
            try:
                with transaction.atomic(using="default"):
                    RelationShipProfile.objects.filter(
                        to_profile=recipient, from_profile=emitter, type=FOLLOWING
                    ).delete()
                    RelationShipProfile.objects.filter(
                        to_profile=emitter, from_profile=recipient, type=FOLLOWING
                    ).delete()
                status = "isfollow"
            except Exception as e:
                logger.info(e)
                response = False
                data = {"response": response, "haslike": haslike, "status": status}
                return HttpResponse(json.dumps(data), content_type="application/json")

        # Ver si hay una peticion de "seguir" pendiente (al perfil contrario)
        try:
            follow_request_reverse = Request.objects.get_follow_request(
                from_profile=n.user_id, to_profile=m.user_id
            )
        except ObjectDoesNotExist:
            follow_request_reverse = None

        if follow_request_reverse:
            Request.objects.remove_received_follow_request(
                from_profile=n.user_id, to_profile=m.user_id
            )

        # Ver si seguimos al perfil que vamos a bloquear

        if RelationShipProfile.objects.is_follow(
            from_profile=recipient, to_profile=emitter
        ):
            try:
                with transaction.atomic(using="default"):
                    RelationShipProfile.objects.filter(
                        to_profile=emitter, from_profile=recipient, type=FOLLOWING
                    ).delete()
                    RelationShipProfile.objects.filter(
                        to_profile=recipient, from_profile=emitter, type=FOLLOWING
                    ).delete()
            except Exception as e:
                logger.info(e)
                response = False
                data = {"response": response, "haslike": haslike, "status": status}
                return HttpResponse(json.dumps(data), content_type="application/json")

        try:
            RelationShipProfile.objects.create(
                to_profile=recipient, from_profile=emitter, type=BLOCK
            )
        except Exception as e:
            logger.info(e)
            response = False
            data = {"response": response, "haslike": haslike, "status": status}
            return HttpResponse(json.dumps(data), content_type="application/json")

        response = True
        print("response: %s, haslike: %s, status: %s" % (response, haslike, status))
        data = {"response": response, "haslike": haslike, "status": status}
        return HttpResponse(json.dumps(data), content_type="application/json")


@login_required(login_url="/")
def welcome_view(request, username):
    """
    View para pagina de bienvenida despues
    del registro.
    """
    user_profile = get_object_or_404(User, username__iexact=username)
    user = request.user

    if user_profile.pk != user.pk:
        raise Http404

    return render(request, "account/nuevosusuarios.html", {"user_profile": user})


@login_required(login_url="/")
@ensure_csrf_cookie
def welcome_step_1(request):
    """
    View para seleccionar los intereses
    del usuario registrado.
    """
    user = request.user

    user_profile = user.profile

    context = {"user_profile": user}

    if request.method == "POST":
        response = "success"

        tags = request.POST.getlist("tags[]")
        choices = request.POST.getlist("choices[]")
        choices = [
            dict(ThemesForm.CHOICES).get(choice, "").lower() for choice in choices
        ]
        interests = union_without_duplicates(tags, choices)

        for tag in interests:
            if tag.isspace():
                response = "with_spaces"
                return HttpResponse(
                    json.dumps(response), content_type="application/json"
                )

            tag = tag.lower()

            interest_exists = user_profile.tags.filter(name__iexact=tag).exists()

            if not interest_exists and tag:
                user_profile.tags.add(tag)

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        context["top_tags"] = Profile.tags.most_common()[:10]
        context["form"] = ThemesForm

    return render(request, "account/welcomestep1.html", context)


@login_required(login_url="/")
def set_first_Login(request):
    """
    Establece si el usuario se ha logueado por primera vez
    """
    print(">>> SET_FIRST_LOGIN")
    user = request.user
    if request.method == "POST":
        print(">>> IS_POST")
        if user.profile.is_first_login:
            user.profile.is_first_login = False
    else:  # ON GET ETC...
        return redirect("user_profile:profile", username=user.username)


class RecommendationUsers(ListView):
    """
        Lista de usuarios recomendados segun
        los intereses del usuario.
    """

    model = User
    template_name = "account/reccomendation_after_login.html"

    def __init__(self, *args, **kwargs):
        super(RecommendationUsers, self).__init__(*args, **kwargs)
        self.pagination = None

    def get_queryset(self):
        user = self.request.user
        current_page = int(self.request.GET.get("page", "1"))  # page or 1
        limit = 25 * current_page
        offset = limit - 25

        users = (
            Profile.objects.filter(
                ~Q(user=user)
                & Q(tags__in=user.profile.tags.all())
                & ~Q(privacity="N")
                & Q(user__is_active=True)
            )
            .annotate(similarity=Count("tags"))
            .order_by("-similarity")
            .select_related("user")[offset:limit]
        )
        print(users)
        if not users:
            users = Profile.objects.filter(~Q(user=user) & ~Q(privacity="N")).order_by(
                "?"
            )[:25]

        total_users = (
            Profile.objects.exclude(
                user=self.request.user, privacity="N", user__is_active=False
            )
            .filter(tags__in=user.profile.tags.all())
            .count()
        )

        total_pages = int(total_users / 25)
        if total_users % 25 != 0:
            total_pages += 1
        self.pagination = make_pagination_html(current_page, total_pages)

        return users

    def get_context_data(self, **kwargs):
        context = super(RecommendationUsers, self).get_context_data(**kwargs)
        context["user_profile"] = self.request.user
        context["pagination"] = self.pagination
        return context


recommendation_users = login_required(RecommendationUsers.as_view(), login_url="/")


class LikeListUsers(TemplateView):
    """
    Lista de usuarios que han dado like a un perfil
    """

    template_name = "account/like_list.html"

    def __init__(self, *args, **kwargs):
        super(LikeListUsers, self).__init__(*args, **kwargs)
        self.pagination = None

    @method_decorator(user_can_view_profile_info)
    def dispatch(self, request, *args, **kwargs):
        return super(LikeListUsers, self).dispatch(request, *args, **kwargs)

    def _get_skyfolk_card_of_like_profiles(self, users):
        ct = ContentType.objects.get_for_model(Profile)
        ids = [result.from_profile.id for result in users]

        following_result = []

        videos = (
            Video.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(videos_count=Count("owner__profile__id"))
            .values("owner__profile__id", "videos_count")
            .order_by()
        )
        photos = (
            Photo.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(photos_count=Count("owner__profile__id"))
            .values("owner__profile__id", "photos_count")
            .order_by()
        )
        followers_result = (
            RelationShipProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(follower_count=Count("to_profile_id"))
            .values("follower_count", "to_profile_id")
            .order_by()
        )
        likes = (
            LikeProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(likes_count=Count("to_profile_id"))
            .order_by()
        )
        total_exp = (
            Award.objects.filter(user__profile__id__in=ids)
            .values("user_id")
            .annotate(exp_count=Sum("badge__points"))
            .values("user_id", "exp_count")
            .order_by()
        )
        last_ranks = (
            UserRank.objects.filter(users__id__in=ids)
            .values("users__id")
            .order_by("-reached_with")
            .values("users__id", "name", "description")
        )

        seen = set()
        last_ranks = [
            last_rank
            for last_rank in last_ranks
            if [last_rank["users__id"] not in seen, seen.add(last_rank["users__id"])][0]
        ]

        for like_profile in users:
            tagged_items = TaggedItem.objects.filter(
                content_type=ct, object_id=like_profile.from_profile.id
            ).select_related("tag")[:10]
            tags = [tag.tag for tag in tagged_items]
            count_videos = next(
                iter(
                    [
                        video["videos_count"]
                        for video in videos
                        if video["owner__profile__id"] == like_profile.from_profile.id
                    ]
                    or []
                ),
                0,
            )

            count_photos = next(
                iter(
                    [
                        photo["photos_count"]
                        for photo in photos
                        if photo["owner__profile__id"] == like_profile.from_profile.id
                    ]
                    or []
                ),
                0,
            )

            followers = next(
                iter(
                    [
                        follower["follower_count"]
                        for follower in followers_result
                        if follower["to_profile_id"] == like_profile.from_profile.id
                    ]
                    or []
                ),
                0,
            )
            count_likes = next(
                iter(
                    [
                        like["likes_count"]
                        for like in likes
                        if like["to_profile_id"] == like_profile.from_profile.id
                    ]
                    or []
                ),
                0,
            )

            exp = next(
                iter(
                    [
                        exp["exp_count"]
                        for exp in total_exp
                        if exp["user_id"] == like_profile.from_profile.id
                    ]
                    or []
                ),
                0,
            )

            last_rank = next(
                iter(
                    [
                        last_rank
                        for last_rank in last_ranks
                        if like_profile.from_profile.user_id == last_rank["users__id"]
                    ]
                    or []
                ),
                {},
            )

            skyfolk_card_id = FactorySkyfolkCardIdentifier.create()
            skyfolk_card_id.id = like_profile.from_profile.id
            skyfolk_card_id.profile = like_profile.from_profile
            skyfolk_card_id.tags = tags
            skyfolk_card_id.last_rank = last_rank
            skyfolk_card_id.videos = count_videos
            skyfolk_card_id.photos = count_photos
            skyfolk_card_id.likes = count_likes
            skyfolk_card_id.followers = followers
            skyfolk_card_id.exp = exp

            following_result.append(skyfolk_card_id)

        return following_result

    def _get_like_profile(self, page, username):
        try:
            profile = Profile.objects.get(user__username=username)
        except ObjectDoesNotExist:
            raise Http404

        paginator = Paginator(
            LikeProfile.objects.filter(to_profile=profile).select_related(
                "from_profile", "from_profile__user"
            ),
            25,
        )

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        return users

    def get_context_data(self, **kwargs):
        context = super(LikeListUsers, self).get_context_data(**kwargs)
        page = self.request.GET.get("page", 1)
        username = self.kwargs.get("username")
        likes_profile = self._get_like_profile(page, username)
        context["object_list"] = self._get_skyfolk_card_of_like_profiles(likes_profile)
        context["likes_profile"] = likes_profile
        context["user_profile"] = self.kwargs["username"]
        return context


like_list = login_required(LikeListUsers.as_view(), login_url="/")


def autocomplete(request):
    """
    Autocompletado de usuarios
    """
    q = request.GET.get("q", "")

    try:
        sqs = (
            Profile.objects.filter(
                Q(user__username__istartswith=q)
                | Q(user__last_name__istartswith=q)
                | Q(user__first_name__istartswith=q)
            )
            .values("user__username", "user__last_name", "user__first_name")
            .distinct()[:7]
        )
        suggestions = [
            {
                "username": result["user__username"],
                "first_name": result["user__first_name"],
                "last_name": result["user__last_name"],
                "avatar": avatar(result["user__username"]),
            }
            for result in sqs
        ]
        the_data = json.dumps({"results": suggestions})
    except RequestError as e:
        the_data = json.dumps({"results": []})
        logger.info("Error al buscar q: {} - ERROR: {}".format(q, e))

    return HttpResponse(the_data, content_type="application/json")


class SearchView(TemplateView):
    template_name = "search/search.html"
    form_class = SearchForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.models = []

        criteria = self.kwargs.get("option", "all")
        q = self.request.GET.get("q", "")

        self.initial = {"q": q, "s": criteria}

        if criteria == "all":
            self.models.append(Profile)
            self.models.append(Publication)
            self.models.append(Photo)
            self.models.append(Video)
            self.models.append(UserGroups)
        if criteria == "accounts":
            self.models.append(Profile)
        if criteria == "publications":
            self.models.append(Publication)
        if criteria == "images":
            self.models.append(Photo)
        if criteria == "videos":
            self.models.append(Video)
        if criteria == "groups":
            self.models.append(UserGroups)

        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET.get("q", "")
        page = self.request.GET.get("page", 1)
        profile = Profile.objects.get(user_id=self.request.user.id)

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=profile, type=BLOCK
        ).values("from_profile_id")

        following = RelationShipProfile.objects.filter(
            Q(from_profile=profile) & ~Q(type=BLOCK)
        ).values("to_profile_id")
        followers = RelationShipProfile.objects.filter(
            Q(to_profile=profile) & ~Q(type=BLOCK)
        ).values("from_profile_id")

        photo_results = []
        video_results = []
        profile_results = []
        groups_results = []
        publications_results = []

        for model in self.models:
            if model == Photo:
                photo_results = self._get_photos(
                    followers, following, users_not_blocked_me, q
                )
            elif model == Video:
                video_results = self._get_videos(
                    followers, following, users_not_blocked_me, q
                )
            elif model == Profile:
                profile_results = self._get_profiles(q)
            elif model == UserGroups:
                groups_results = self._get_groups(q)
            elif model == Publication:
                publications_results = self._get_publications(
                    followers, following, users_not_blocked_me, q
                )

        result = list(
            sorted(
                chain(
                    photo_results,
                    video_results,
                    profile_results,
                    groups_results,
                    publications_results,
                ),
                key=lambda objects: objects.id,
                reverse=True,
            )
        )
        paginator = Paginator(result, 50)

        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        return results

    def _get_publications(self, followers, following, users_not_blocked_me, q):
        q_object = Q(content__icontains=q) | Q(author__username__iexact=q)
        return (
            Publication.objects.filter(
                q_object
                & (
                    (
                        Q(board_owner_id=self.request.user.id)
                        | Q(author_id=self.request.user.id)
                    )
                    | (
                        (
                            ~Q(board_owner__profile__in=users_not_blocked_me)
                            & ~Q(board_owner__profile__privacity="N")
                            & ~Q(author__profile__in=users_not_blocked_me)
                        )
                        & (
                            (
                                Q(board_owner__profile__privacity="A")
                                | (
                                    (
                                        Q(board_owner__profile__privacity="OF")
                                        & Q(board_owner__profile__in=following)
                                    )
                                    | (
                                        Q(board_owner__profile__privacity="OFAF")
                                        & (
                                            Q(board_owner__profile__in=following)
                                            | Q(board_owner__profile__in=followers)
                                        )
                                    )
                                )
                                & (
                                    (
                                        Q(author__profile__privacity="OF")
                                        & Q(author__profile__in=following)
                                    )
                                    | (
                                        Q(author__profile__privacity="OFAF")
                                        & (
                                            Q(author__profile__in=following)
                                            | Q(author__profile__in=followers)
                                        )
                                    )
                                    | Q(author__profile__privacity="A")
                                )
                            )
                            | (
                                Q(author__profile__privacity="A")
                                | (
                                    (
                                        Q(author__profile__privacity="OF")
                                        & Q(author__profile__in=following)
                                    )
                                    | (
                                        Q(author__profile__privacity="OFAF")
                                        & (
                                            Q(author__profile__in=following)
                                            | Q(author__profile__in=followers)
                                        )
                                    )
                                )
                                & (
                                    (
                                        Q(board_owner__profile__privacity="OF")
                                        & Q(board_owner__profile__in=following)
                                    )
                                    | (
                                        Q(board_owner__profile__privacity="OFAF")
                                        & (
                                            Q(board_owner__profile__in=following)
                                            | Q(board_owner__profile__in=followers)
                                        )
                                    )
                                    | Q(board_owner__profile__privacity="A")
                                )
                            )
                        )
                    )
                )
            )
            .select_related(
                "author",
                "board_owner",
                "shared_publication",
                "parent",
                "shared_group_publication",
            )
            .prefetch_related(
                "extra_content",
                "images",
                "videos",
                "shared_publication__images",
                "tags",
                "shared_publication__author",
                "shared_group_publication__images",
                "shared_group_publication__author",
                "shared_group_publication__videos",
                "shared_group_publication__extra_content",
                "shared_publication__videos",
                "shared_publication__extra_content",
            )
            .filter(deleted=False)
            .distinct()
            .order_by("-created")[:3000]
        )

    def _get_groups(self, q):
        q_object = Q(name__icontains=q) | Q(description__icontains=q) | Q(tags__name=q)
        return UserGroups.objects.filter(q_object).distinct()[:3000]

    def _get_profiles(self, q):
        q_object = (
            Q(user__username__iexact=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(tags__name=q)
        )
        qs = Profile.objects.filter(
            q_object & (Q(user__is_active=True) & ~Q(privacity="N"))
        ).distinct()[:3000]
        ct = ContentType.objects.get_for_model(Profile)
        ids = [result.id for result in qs]

        following_result = []

        videos = (
            Video.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(videos_count=Count("owner__profile__id"))
            .values("owner__profile__id", "videos_count")
            .order_by()
        )
        photos = (
            Photo.objects.filter(owner__profile__id__in=ids)
            .values("owner__profile__id")
            .annotate(photos_count=Count("owner__profile__id"))
            .values("owner__profile__id", "photos_count")
            .order_by()
        )
        followers_result = (
            RelationShipProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(follower_count=Count("to_profile_id"))
            .values("follower_count", "to_profile_id")
            .order_by()
        )
        likes = (
            LikeProfile.objects.filter(to_profile__id__in=ids)
            .values("to_profile_id")
            .annotate(likes_count=Count("to_profile_id"))
            .order_by()
        )
        total_exp = (
            Award.objects.filter(user__profile__id__in=ids)
            .values("user_id")
            .annotate(exp_count=Sum("badge__points"))
            .values("user_id", "exp_count")
            .order_by()
        )
        last_ranks = (
            UserRank.objects.filter(users__id__in=ids)
            .values("users__id")
            .order_by("-reached_with")
            .values("users__id", "name", "description")
        )

        seen = set()
        last_ranks = [
            last_rank
            for last_rank in last_ranks
            if [last_rank["users__id"] not in seen, seen.add(last_rank["users__id"])][0]
        ]

        for follow in qs:
            tagged_items = TaggedItem.objects.filter(
                content_type=ct, object_id=follow.id
            ).select_related("tag")[:10]
            tags = [tag.tag for tag in tagged_items]
            count_videos = next(
                iter(
                    [
                        video["videos_count"]
                        for video in videos
                        if video["owner__profile__id"] == follow.id
                    ]
                    or []
                ),
                0,
            )

            count_photos = next(
                iter(
                    [
                        photo["photos_count"]
                        for photo in photos
                        if photo["owner__profile__id"] == follow.id
                    ]
                    or []
                ),
                0,
            )

            followers = next(
                iter(
                    [
                        follower["follower_count"]
                        for follower in followers_result
                        if follower["to_profile_id"] == follow.id
                    ]
                    or []
                ),
                0,
            )
            count_likes = next(
                iter(
                    [
                        like["likes_count"]
                        for like in likes
                        if like["to_profile_id"] == follow.id
                    ]
                    or []
                ),
                0,
            )

            exp = next(
                iter(
                    [
                        exp["exp_count"]
                        for exp in total_exp
                        if exp["user_id"] == follow.id
                    ]
                    or []
                ),
                0,
            )

            last_rank = next(
                iter(
                    [
                        last_rank
                        for last_rank in last_ranks
                        if follow.user_id == last_rank["users__id"]
                    ]
                    or []
                ),
                {},
            )

            skyfolk_card_id = FactorySkyfolkCardIdentifier.create()
            skyfolk_card_id.id = follow.id
            skyfolk_card_id.profile = follow
            skyfolk_card_id.tags = tags
            skyfolk_card_id.last_rank = last_rank
            skyfolk_card_id.videos = count_videos
            skyfolk_card_id.photos = count_photos
            skyfolk_card_id.likes = count_likes
            skyfolk_card_id.followers = followers
            skyfolk_card_id.exp = exp

            following_result.append(skyfolk_card_id)

        return following_result

    def _get_videos(self, followers, following, users_not_blocked_me, q):
        q_object = (
            Q(owner__username__iexact=q)
            | Q(owner__first_name__iexact=q)
            | Q(owner__last_name__icontains=q)
            | Q(name__icontains=q)
            | Q(tags__name=q)
        )
        return (
            Video.objects.filter(
                q_object
                & (
                    Q(owner_id=self.request.user.id)
                    | (
                        (
                            ~Q(owner__profile__privacity="N")
                            & ~Q(owner__profile__in=users_not_blocked_me)
                        )
                        & (
                            (
                                Q(owner__profile__privacity="OF")
                                & Q(owner__profile__in=following)
                                & Q(is_public=True)
                            )
                            | (Q(owner__profile__privacity="A") & Q(is_public=True))
                            | (
                                Q(owner__profile__privacity="OFAF")
                                & (
                                    Q(owner__profile__in=following)
                                    | Q(owner__profile__in=followers)
                                )
                            )
                        )
                    )
                )
            )
            .select_related("owner")
            .prefetch_related("tags")
            .order_by("-date_added")
            .distinct()[:3000]
        )

    def _get_photos(self, followers, following, users_not_blocked_me, q):
        q_object = (
            Q(owner__username__iexact=q)
            | Q(owner__first_name__iexact=q)
            | Q(owner__last_name__icontains=q)
            | Q(title__icontains=q)
            | Q(tags__name=q)
        )
        return (
            Photo.objects.filter(
                q_object
                & (
                    Q(owner_id=self.request.user.id)
                    | (
                        (
                            ~Q(owner__profile__privacity="N")
                            & ~Q(owner__profile__in=users_not_blocked_me)
                        )
                        & (
                            (
                                Q(owner__profile__privacity="OF")
                                & Q(owner__profile__in=following)
                                & Q(is_public=True)
                            )
                            | (Q(owner__profile__privacity="A") & Q(is_public=True))
                            | (
                                Q(owner__profile__privacity="OFAF")
                                & (
                                    Q(owner__profile__in=following)
                                    | Q(owner__profile__in=followers)
                                )
                            )
                        )
                    )
                )
            )
            .select_related("owner")
            .prefetch_related("tags")
            .order_by("-date_added")
            .distinct()[:3000]
        )

    def get_context_data(self, **kwargs):
        ctx = super(SearchView, self).get_context_data(**kwargs)

        try:
            ctx["tab"] = self.kwargs["option"]
        except KeyError:
            ctx["tab"] = "all"

        ctx["searchForm"] = self.form_class(self.initial)
        ctx["q"] = self.initial.get("q")
        ctx["s"] = self.initial.get("s")
        ctx["object_list"] = self.get_queryset()
        return ctx


@login_required(login_url="/")
def recommendation_real_time(request):
    if request.method == "POST":
        try:
            ids = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"response": None})

        if len(ids) > 100:
            ids = []

        user_profile = request.user.profile

        sql_result = (
            Profile.objects.filter(
                ~Q(user=user_profile.user)
                & Q(tags__in=user_profile.tags.all())
                & ~Q(privacity="N")
                & Q(user__is_active=True)
                & ~Q(user_id__in=ids)
            )
            .annotate(similarity=Count("tags"))
            .select_related("user")
            .order_by("-similarity")[:50]
        )

        sql_users = [
            {
                "id": u.id,
                "username": u.user.username,
                "first_name": u.user.first_name,
                "last_name": u.user.last_name,
                "avatar": avatar_url(u.user),
            }
            for u in sql_result
        ]
        return JsonResponse(sql_users, safe=False)

    return JsonResponse({"response": None})


# class FollowingByAffinityList(generics.ListAPIView):
#     serializer_class = UserSerializer
#     renderer_classes = (JSONRenderer,)
#
#     def get_queryset(self):
#         user = self.request.user
#         n = NodeProfile.nodes.get(title=user.username)
#         usernames = [u.title for u in n.get_favs_users()]
#         preserved = Case(*[When(username=username, then=pos) for pos, username in enumerate(usernames)])
#         return User.objects.filter(username__in=usernames).order_by(preserved)
#
#
# class FollowersByAffinityList(generics.ListAPIView):
#     serializer_class = UserSerializer
#     renderer_classes = (JSONRenderer,)
#
#     def get_queryset(self):
#         user = self.request.user
#         return RelationShipProfile.objects.filter(to_profile=user.profile) \
#             .order_by("-weight")[:10] \
#             .select_related("from_profile__user")


class NotificationSettingsView(AjaxableResponseMixin, UpdateView):
    model = NotificationSettings
    template_name = "account/cf-notifications.html"
    fields = [
        "email_when_new_notification",
        "email_when_recommendations",
        "email_when_mp",
        "followed_notifications",
        "followers_notifications",
        "only_confirmed_users",
    ]
    success_url = "/config/notifications/"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationSettingsView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(NotificationSettings, user_id=self.request.user.id)

    def form_valid(self, form, msg=None):
        instance = form.save(commit=False)
        instance.user = self.request.user
        return super(NotificationSettingsView, self).form_valid(form)


class UserLikeContent(TemplateView):
    """
    Like user content show here
    """

    template_name = "user_profile/user_content.html"

    def __init__(self, *args, **kwargs):
        super(UserLikeContent, self).__init__(*args, **kwargs)
        self.pagination = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserLikeContent, self).dispatch(request, *args, **kwargs)

    def get_like_content(self):
        current_page = int(self.request.GET.get("page", "1"))  # page or 1
        limit = 25 * current_page
        offset = limit - 25

        user = self.request.user
        publications = (
            Publication.objects.filter(user_give_me_like__id__exact=user.id)
            .select_related("author")
            .prefetch_related("images")[offset:limit]
        )
        users = LikeProfile.objects.filter(from_profile__user=user).select_related(
            "to_profile__user"
        )[offset:limit]
        groups = LikeGroup.objects.filter(from_like=user).select_related("to_like")[
            offset:limit
        ]

        mixed = list(
            sorted(
                chain.from_iterable(
                    [
                        filter(None, zipped)
                        for zipped in zip_longest(publications, users, groups)
                    ]
                ),
                key=lambda objects: objects.created,
                reverse=True,
            )
        )

        total_pubs = np.size(publications)
        total_users = np.size(users)
        total_groups = np.size(groups)

        if total_pubs >= 25 or total_users >= 25 or total_groups >= 25:
            self.pagination = current_page + 1
        else:
            self.pagination = None

        return mixed

    def get_context_data(self, **kwargs):
        context = super(UserLikeContent, self).get_context_data(**kwargs)
        context["mixed"] = self.get_like_content()
        context["pagination"] = self.pagination
        return context


FORMS = [("user", UsernameForm), ("email", EmailForm)]

TEMPLATES = {"user": "account/username_form.html", "email": "account/email_signup.html"}


class CustomSignupView(
    RedirectAuthenticatedUserMixin, CloseableSignupMixin, SessionWizardView
):
    form_list = FORMS
    template_name = "account/signup.html"
    redirect_field_name = "next"
    success_url = None

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(CustomSignupView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(self.request, self.redirect_field_name)
            or self.success_url
        )
        return ret

    def done(self, form_list, **kwargs):
        i = 0

        user_fields = {}
        for form in form_list:
            data = form.cleaned_data
            if i == 0:
                user_fields["username"] = data["username"]
                user_fields["password"] = data["password1"]
            elif i == 1:
                user_fields["email"] = data["email"]

            i += 1

        user = User.objects.create_user(
            username=user_fields["username"],
            email=user_fields["email"],
            password=user_fields["password"],
        )
        try:
            return complete_signup(
                self.request,
                user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url(),
            )
        except ImmediateHttpResponse as e:
            return e.response


signup = CustomSignupView.as_view()


def page_not_found(request, exception, template_name="account/404.html"):
    context = {"error_code": 404}
    return render(request, template_name, context, status=404)


def server_error(request, template_name="account/500.html"):
    return render(request, template_name, status=500)


def permission_denied(request, exception, template_name="account/403.html"):
    return render(request, template_name, status=403)


def bad_request(request, exception, template_name="account/400.html"):
    return render(request, template_name, status=400)


def csrf_failure(request, reason="", template_name="account/403_csrf.html"):
    return render(request, template_name, status=403)
