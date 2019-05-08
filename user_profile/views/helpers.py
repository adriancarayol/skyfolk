from django.core.exceptions import ViewDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import OuterRef, Count, Value, Case, When, Q, IntegerField, Subquery
from django.http import Http404
from django.shortcuts import render

from dash.base import get_layout
from dash.helpers import iterable_to_dict
from dash.models import DashboardEntry
from dash.utils import get_dashboard_settings, get_user_plugins, get_workspaces, get_public_dashboard_url
from publications.models import Publication
from user_profile.constants import BLOCK
from user_profile.models import RelationShipProfile

from loguru import logger


# TODO: Make generic
def load_anonymous_profile_publications(request, page, profile):
    shared_publications = (
        Publication.objects.filter(shared_publication__id=OuterRef("pk"), deleted=False)
            .order_by()
            .values("shared_publication__id")
    )

    total_shared_publications = shared_publications.annotate(c=Count("*")).values("c")

    pubs = (
        Publication.objects.filter(
            Q(board_owner_id=profile.id)
            & Q(level__lte=0)
            & Q(deleted=False)
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
            .select_related(
            "author",
            "board_owner",
            "shared_publication",
            "parent",
            "shared_group_publication",
        ).annotate(likes=Count("user_give_me_like"), hates=Count("user_give_me_hate")).annotate(
            total_shared=Subquery(
                total_shared_publications, output_field=IntegerField()
            )
        )
    )


def load_profile_publications(request, page, profile):
    """
    Devuelve los comentarios de un perfil
    """
    user = request.user

    shared_publications = (
        Publication.objects.filter(shared_publication__id=OuterRef("pk"), deleted=False)
            .order_by()
            .values("shared_publication__id")
    )

    total_shared_publications = shared_publications.annotate(c=Count("*")).values("c")

    shared_for_me = shared_publications.annotate(
        have_shared=Count(Case(When(author_id=user.id, then=Value(1))))
    ).values("have_shared")

    users_not_blocked_me = RelationShipProfile.objects.filter(
        to_profile=user.profile, type=BLOCK
    ).values("from_profile_id")

    pubs = (
        Publication.objects.filter(
            ~Q(author__profile__in=users_not_blocked_me)
            & Q(board_owner_id=profile.id)
            & Q(level__lte=0)
            & Q(deleted=False)
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
            .select_related(
            "author",
            "board_owner",
            "shared_publication",
            "parent",
            "shared_group_publication",
        )
            .annotate(likes=Count("user_give_me_like"), hates=Count("user_give_me_hate"))
            .annotate(
            have_like=Count(
                Case(
                    When(user_give_me_like__id=user.id, then=Value(1)),
                    output_field=IntegerField(),
                )
            ),
            have_hate=Count(
                Case(
                    When(user_give_me_hate__id=user.id, then=Value(1)),
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
    )

    try:
        paginator = Paginator(pubs, 25)
        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

    except Exception as e:
        publications = []
        logger.info(e)

    return publications


def profile_view_ajax(request, user_profile, node_profile=None):
    """
    Vista AJAX para paginacion
    de la vista profile
    """

    qs = request.GET.get("qs", None)

    if not qs:
        raise ViewDoesNotExist("Parametro QS no encontrado")

    if qs == "publications":
        page = request.GET.get("page", 1)
        template = "account/profile_comments.html"
        publications = load_profile_publications(request, page, user_profile)
        context = {"user_profile": user_profile, "publications": publications}
    else:
        raise ValueError("No existe el querystring %s" % qs[:25])

    return render(request, template_name=template, context=context)


def fill_profile_dashboard(request, user, username, context):
    dashboard_settings = get_dashboard_settings(username)

    if dashboard_settings:
        layout = get_layout(layout_uid=dashboard_settings.layout_uid, as_instance=True)
    else:
        raise Http404

    registered_plugins = get_user_plugins(user)
    user_plugin_uids = [uid for uid, repr in registered_plugins]
    logger.debug(user_plugin_uids)

    entries_q = Q(user=user, layout_uid=layout.uid, workspace=None)

    dashboard_entries = (
        DashboardEntry._default_manager.filter(entries_q)
            .select_related("workspace", "user")
            .order_by("placeholder_uid", "position")[:]
    )

    placeholders = layout.get_placeholder_instances(dashboard_entries, request=request)

    layout.collect_widget_media(dashboard_entries)

    context["js"] = layout.get_media_js()
    context["layout"] = layout
    context["dashboard_settings"] = dashboard_settings
    context["placeholders"] = placeholders
    context["placeholders_dict"] = iterable_to_dict(placeholders, key_attr_name="uid")

    workspaces = get_workspaces(user, layout.uid, None, public=True)

    context.update(workspaces)

    context.update(
        {"public_dashboard_url": get_public_dashboard_url(dashboard_settings)}
    )
