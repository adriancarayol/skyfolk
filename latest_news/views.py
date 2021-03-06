from itertools import chain, zip_longest

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count
from django.views.generic import ListView
from dash.models import DashboardEntry
from photologue.models import Photo, Video
from publications.models import Publication
from user_profile.models import Profile, RelationShipProfile
from user_profile.constants import BLOCK
from dash.base import get_layout


class BaseNews(ListView):
    template_name = "account/base_news.html"
    context_object_name = "publications"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pagination = None
        self.layout = get_layout(layout_uid="profile", as_instance=True)

    def get_affinity_users(self):
        """
        Devuelve los 6 perfiles favoritos del usuario
        """
        raise NotImplementedError

    def get_recommendation_users(self):
        raise NotImplementedError

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class AnonymousUserNews(BaseNews):
    def get_affinity_users(self):
        return ()

    def get_recommendation_users(self, offset=0, limit=25):
        return ()

    def get_queryset(self):
        current_page = int(self.request.GET.get("page", "1"))  # page or 1
        limit = 50 * current_page
        offset = limit - 50
        publications = Publication.objects.filter(
            Q(board_owner__profile__privacity="A")
            & Q(author__profile__privacity="A")
        ).annotate(likes=Count('user_give_me_like')).order_by('-likes', '-created')[offset:limit]

        photos = Photo.objects.filter(
            Q(owner__profile__privacity="A") & Q(is_public=True)
        ).order_by("-date_added")[offset:limit]
        videos = Video.objects.filter(
            Q(owner__profile__privacity="A") & Q(is_public=True)
        ).order_by("-date_added")[offset:limit]
        entries_q = Q(user__profile__privacity="A") & Q(
            layout_uid="profile", workspace=None
        )

        dashboard_entries = (
            DashboardEntry._default_manager.filter(entries_q)
                .select_related("workspace", "user")
                .order_by("placeholder_uid", "position")[offset:limit]
        )

        placeholders = self.layout.get_placeholder_instances(
            dashboard_entries, request=self.request
        )

        self.layout.collect_widget_media(dashboard_entries)

        result_list = list(
            chain.from_iterable(
                [
                    filter(None, zipped)
                    for zipped in zip_longest(
                    publications, photos, videos, placeholders
                )
                ]
            )
        )

        return result_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["component"] = "recommendations.js"
        context["js"] = self.layout.get_media_js()
        return context


class AuthUserNews(BaseNews):

    def get_affinity_users(self):
        """
        Devuelve los 6 perfiles favoritos del usuario
        """
        return (
            RelationShipProfile.objects.filter(from_profile=self.request.user.profile)
                .order_by("-weight")[:10]
                .select_related("to_profile__user")
        )

    def get_recommendation_users(self, offset=0, limit=25):
        user_profile = self.request.user.profile

        return (
            Profile.objects.filter(
                ~Q(user=user_profile.user)
                & Q(tags__in=user_profile.tags.all())
                & ~Q(privacity="N")
                & Q(user__is_active=True)
            )
                .annotate(similarity=Count("tags"))
                .order_by("-similarity")
                .values_list("user_id", flat=True)[offset:limit]
        )

    def get_queryset(self):
        current_page = int(self.request.GET.get("page", "1"))  # page or 1
        limit = 50 * current_page
        offset = limit - 50

        try:
            profile = Profile.objects.get(user_id=self.request.user.id)
        except Exception as e:
            raise ValueError(
                "El perfil de {user} no existe, {e}".format(user=self.request.user, e=e)
            )

        # ids de usuarios recomendados
        pk_list = self.get_recommendation_users(offset=offset, limit=limit)

        # Usuarios que me tienen bloqueado
        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=profile, type=BLOCK
        ).values("from_profile_id")

        # Usuarios a los que sigo
        following = RelationShipProfile.objects.filter(
            Q(from_profile=profile) & ~Q(type=BLOCK)
        ).values("to_profile_id")

        # Publicaciones de seguidos + favoritos + recomendados
        try:
            publications = (
                Publication.objects.filter(
                    (
                            (
                                    Q(board_owner__profile__in=following)
                                    | Q(board_owner_id__in=pk_list)
                            )
                            & (
                                    ~Q(author__profile__in=users_not_blocked_me)
                                    & ~Q(board_owner__profile__in=users_not_blocked_me)
                                    & ~Q(board_owner__profile__privacity="N")
                                    & ~Q(author__profile__privacity="N")
                                    & ~Q(author_id=self.request.user.id)
                            )
                    )
                    & Q(deleted=False)
                    & Q(parent=None)
                )
                    .select_related(
                    "author", "shared_publication", "parent", "shared_group_publication"
                )
                    .prefetch_related(
                    "extra_content",
                    "images",
                    "videos",
                    "shared_publication__extra_content",
                    "shared_publication__images",
                    "shared_publication__videos",
                    "shared_group_publication__images",
                    "shared_group_publication__author",
                    "shared_group_publication__videos",
                    "shared_group_publication__extra_content",
                    "shared_publication__author",
                )
                    .distinct()[offset:limit]
            )
        except ObjectDoesNotExist:
            publications = Publication.objects.filter(
                Q(board_owner__profile__privacity="A")
                & Q(author__profile__privacity="A")
            )[offset:limit]

        # Photos de seguidos + favoritos + recomendados
        try:
            photos = (
                Photo.objects.filter(
                    (
                            (Q(owner__profile__in=following) | Q(owner_id__in=pk_list))
                            & ~Q(owner__profile__in=users_not_blocked_me)
                    )
                    & Q(is_public=True)
                )
                    .select_related("owner")
                    .prefetch_related("tags")
                    .order_by("-date_added")
                    .distinct()[offset:limit]
            )
        except Photo.DoesNotExist:
            photos = Photo.objects.filter(
                Q(owner__profile__privacity="A") & Q(is_public=True)
            ).order_by("-date_added")[offset:limit]

        # Videos de seguidos + favoritos + recomendados
        try:
            videos = (
                Video.objects.filter(
                    (
                            (Q(owner__profile__in=following) | Q(owner_id__in=pk_list))
                            & ~Q(owner__profile__in=users_not_blocked_me)
                    )
                    & Q(is_public=True)
                )
                    .select_related("owner")
                    .prefetch_related("tags")
                    .order_by("-date_added")
                    .distinct()[offset:limit]
            )
        except Video.DoesNotExist:
            videos = Video.objects.filter(
                Q(owner__profile__privacity="A") & Q(is_public=True)
            ).order_by("-date_added")[offset:limit]

        # Widgets de seguidos + favoritos + recomendados

        try:
            entries_q = (
                    (Q(user_id__in=pk_list) | Q(user__profile__in=following))
                    & Q(layout_uid="profile", workspace=None)
                    & ~Q(user__profile__in=users_not_blocked_me)
            )

            dashboard_entries = (
                DashboardEntry._default_manager.filter(entries_q)
                    .select_related("workspace", "user")
                    .order_by("placeholder_uid", "position")[offset:limit]
            )

            placeholders = self.layout.get_placeholder_instances(
                dashboard_entries, request=self.request
            )
        except Exception as e:
            entries_q = Q(user__profile__privacity="A") & Q(
                layout_uid="profile", workspace=None
            )

            dashboard_entries = (
                DashboardEntry._default_manager.filter(entries_q)
                    .select_related("workspace", "user")
                    .order_by("placeholder_uid", "position")[offset:limit]
            )

            placeholders = self.layout.get_placeholder_instances(
                dashboard_entries, request=self.request
            )

        self.layout.collect_widget_media(dashboard_entries)

        extended_list = []

        if (
                len(photos) <= 0
                or len(publications) <= 0
                or len(videos) <= 0
                or len(placeholders) <= 0
        ):
            extended_list = self.get_recommendation_users(offset)

        if len(photos) <= 0:
            photos = Photo.objects.filter(owner_id__in=extended_list)[offset:limit]

        if len(videos) <= 0:
            videos = Video.objects.filter(owner_id__in=extended_list)[offset:limit]

        if len(publications) <= 0:
            publications = Publication.objects.filter(board_owner_id__in=extended_list)[
                           offset:limit
                           ]

        if len(placeholders) <= 0:
            entries_q = Q(user_id__in=extended_list) & Q(
                layout_uid="profile", workspace=None
            )
            dashboard_entries = (
                DashboardEntry._default_manager.filter(entries_q)
                    .select_related("workspace", "user")
                    .order_by("placeholder_uid", "position")[offset:limit]
            )

            placeholders = self.layout.get_placeholder_instances(
                dashboard_entries, request=self.request
            )

        result_list = list(
            chain.from_iterable(
                [
                    filter(None, zipped)
                    for zipped in zip_longest(
                    publications, photos, videos, placeholders
                )
                ]
            )
        )

        total_pubs = len(publications)
        total_photos = len(photos)
        total_videos = len(videos)
        total_placeholders = len(placeholders)

        if (
                total_pubs >= 50
                or total_photos >= 50
                or total_videos >= 50
                or total_placeholders >= 50
        ):
            self.pagination = current_page + 1
        else:
            self.pagination = None

        return result_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get("page", None)
        if not page:
            mix = self.get_affinity_users()
            context["mix"] = [u.to_profile.user for u in mix]
            context["follows"] = [u.to_profile.user.id for u in mix]
        context["pagination"] = self.pagination
        context["component"] = "recommendations.js"
        context["js"] = self.layout.get_media_js()
        return context


def news_and_updates(request):
    user = request.user
    if user.is_authenticated:
        return AuthUserNews.as_view()(request)

    return AnonymousUserNews.as_view()(request)
