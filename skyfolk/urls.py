from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from user_profile.views import signup
from allauth.account import views as allauth_views
from graphene_django.views import GraphQLView

admin.autodiscover()

# REST Framework
# router = routers.DefaultRouter()
# router.register(r'api/users', views.UserViewSet)
# router.register(r'api/groups', views.GroupViewSet)

handler404 = "user_profile.views.page_not_found"
handler500 = "user_profile.views.server_error"
handler403 = "user_profile.views.permission_denied"
handler400 = "user_profile.views.bad_request"
CSRF_FAILURE_VIEW = "user_profile.views.csrf_failure"

urlpatterns = [
    re_path(r"^$", allauth_views.login),
    # Importamos las URLS del resto de apps:
    re_path(r"^4r2k1otg2zztkigzrtu6/", admin.site.urls),
    re_path(r"^accounts/signup/$", signup, name="account_signup"),
    re_path(r"^accounts/", include("allauth.urls")),  # django-allauth
    # urls support
    re_path(r"^", include("support.urls", namespace="support"), name="support"),
    # urls user_profile
    re_path(
        r"^",
        include("user_profile.urls", namespace="user_profile"),
        name="user_profile",
    ),
    # urls para grupos de usuarios
    re_path(
        r"^", include("user_groups.urls", namespace="user_groups"), name="user_groups"
    ),
    # url publications
    re_path(
        r"^",
        include("publications.urls", namespace="publications"),
        name="publications",
    ),
    re_path(
        r"^group/",
        include("publications_groups.urls", namespace="publications_groups"),
        name="publications_groups",
    ),
    re_path(
        r"^group/multimedia/",
        include(
            "publications_gallery_groups.urls", namespace="publications_gallery_groups"
        ),
        name="publications_gallery_groups",
    ),
    # Publicaciones en imagenes de la galeria
    re_path(
        r"^",
        include("publications_gallery.urls", namespace="publications_gallery"),
        name="publications_gallery",
    ),
    # url novedades e inicio
    re_path(r"^", include("latest_news.urls", namespace="latest_news"), name="news"),
    # url mensajes privados
    # About skyfolk
    re_path(r"^", include("about.urls", namespace="about")),
    # Recomendacion password para usuarios
    re_path(
        r"^tips/password/$",
        TemplateView.as_view(template_name="about/password_recommendation.html"),
    ),
    # Urls para el modulo emoji
    re_path(r"^emoji/", include("emoji.urls", namespace="emoji")),
    # Django-avatar
    re_path(r"^", include("avatar.urls", namespace="avatar")),
    # notificaciones
    re_path(
        "^inbox/notifications/",
        include("notifications.urls", namespace="notifications"),
    ),
    # django-photologue
    re_path(
        r"^", include("photologue.urls", namespace="photologue")
    ),  # original photologue
    re_path(
        r"^group/", include("photologue_groups.urls", namespace="photologue_groups")
    ),  # photologue groups
    re_path(r"^messages/", include("postman.urls", namespace="postman")),
    # django-dash URLs:
    # logros
    re_path(r"^badges/", include("badgify.urls", namespace="badges")),
    re_path(r"^awards/", include("awards.urls", namespace="awards")),
    # invitaciones
    re_path(
        r"^config/invitations/", include("invitations.urls", namespace="invitations")
    ),
    re_path(r"^jsreverse/$", urls_js, name="js_reverse"),
    # ****************************************
    # auth module
    # ****************************************
    re_path(r"^auth/", include("django.contrib.auth.urls")),
    # ****************************************
    # dash
    re_path(r"^dashboard/", include("dash.urls", namespace="dash")),
    # API_REST
    re_path(r"^api/", include("api.urls")),
    re_path(r"^graphql", GraphQLView.as_view(graphiql=False)),
    # user guide
    re_path(r"^user-guide/", include("user_guide.urls")),
    # Feedback contact
    re_path(r"^feedback/", include("feedback.urls", namespace="feedback")),
    # Privacy policy
    re_path(r"^information/", include("information.urls", namespace="information")),
    # external servies (twitter, instagram...)
    path("external/", include("external_services.urls", namespace="external_services")),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
