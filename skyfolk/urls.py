from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from dash_services.forms.wizard import DummyForm, ProviderForm, ConsumerForm, ServicesDescriptionForm
from user_profile.views import signup
from dash_services.views_fbv import logout_view
from dash_services.views_fbv import service_related_triggers_switch_to
from dash_services.views_userservices import UserServiceListView, UserServiceCreateView, UserServiceUpdateView
from dash_services.views_userservices import UserServiceDeleteView, renew_service
from dash_services.views_wizard import UserServiceWizard, finalcallback
from allauth.account import views as allauth_views
from graphene_django.views import GraphQLView

admin.autodiscover()

# REST Framework
# router = routers.DefaultRouter()
# router.register(r'api/users', views.UserViewSet)
# router.register(r'api/groups', views.GroupViewSet)

handler404 = 'user_profile.views.page_not_found'
handler500 = 'user_profile.views.server_error'
handler403 = 'user_profile.views.permission_denied'
handler400 = 'user_profile.views.bad_request'
CSRF_FAILURE_VIEW = 'user_profile.views.csrf_failure'

urlpatterns = [
    re_path(r'^$', allauth_views.login),
    # Importamos las URLS del resto de apps:
    re_path(r'^4r2k1otg2zztkigzrtu6/', admin.site.urls),
    re_path(r"^accounts/signup/$", signup, name="account_signup"),
    re_path(r'^accounts/', include('allauth.urls')),  # django-allauth
    # urls support
    re_path(r'^', include('support.urls', namespace="support"), name="support"),
    # urls user_profile
    re_path(r'^', include('user_profile.urls', namespace="user_profile"), name="user_profile"),
    # urls para grupos de usuarios
    re_path(r'^', include('user_groups.urls', namespace="user_groups"), name="user_groups"),
    # url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
    # {'document_root': settings.MEDIA_ROOT}),
    # url publications
    re_path(r'^', include('publications.urls', namespace="publications"), name="publications"),
    re_path(r'^group/', include('publications_groups.urls', namespace="publications_groups"),
        name="publications_groups"),
    re_path(r'^group/multimedia/', include('publications_gallery_groups.urls', namespace="publications_gallery_groups"),
        name="publications_gallery_groups"),
    # Publicaciones en imagenes de la galeria
    re_path(r'^', include('publications_gallery.urls', namespace="publications_gallery"), name="publications_gallery"),
    # url novedades e inicio
    re_path(r'^', include('latest_news.urls', namespace="latest_news"), name="news"),
    # url mensajes privados

    # About skyfolk
    re_path(r'^', include('about.urls')),
    # Recomendacion password para usuarios
    re_path(r'^tips/password/$', TemplateView.as_view(
        template_name='about/password_recommendation.html')),
    # Importamos las urls de REST Framework
    # url(r'^', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Urls para el modulo emoji
    re_path(r'^emoji/', include('emoji.urls', namespace="emoji")),
    # Django-avatar
    re_path(r'^', include('avatar.urls', namespace="avatar")),
    # notificaciones
    # url('^(?P<username>[\w-]+)/notifications/', include('notifications.urls',
    # namespace='notifications')),
    re_path('^inbox/notifications/', include('notifications.urls',
                                         namespace='notifications')),
    # django-photologue
    re_path(r'^', include('photologue.urls', namespace='photologue')),  # original photologue
    re_path(r'^group/', include('photologue_groups.urls', namespace='photologue_groups')),  # photologue groups
    re_path(r'^messages/', include('postman.urls', namespace='postman')),
    # django-dash URLs:
    # url(r'^dashboard/', include('dash.urls')),
    # url(r'^dash/contrib/plugins/rss-feed/', include('dash.contrib.plugins.rss_feed.urls')),
    # url(r'^contrib/', include('dash.contrib.apps.public_dashboard.urls')),
    # logros
    re_path(r'^badges/', include('badgify.urls', namespace="badges")),
    re_path(r'^awards/', include('awards.urls', namespace="awards")),
    # invitaciones
    re_path(r'^config/invitations/', include('invitations.urls', namespace='invitations')),
    re_path(r'^jsreverse/$', urls_js, name='js_reverse'),
    # ****************************************
    # auth module
    # ****************************************
    re_path(r'^auth/', include('django.contrib.auth.urls')),
    # ****************************************
    # customized logout action
    # ****************************************
    re_path(r'^logout/$', logout_view, name='logout'),

    # ****************************************
    # trigger happy module
    # ****************************************
    # url(r'^th/$', TriggerListView.as_view(), name='base'),
    # url(r'^th/trigger/filter_by/(?P<trigger_filtered_by>[a-zA-Z]+)$', TriggerListView.as_view(),
    #     name='trigger_filter_by'),
    # url(r'^th/trigger/order_by/(?P<trigger_ordered_by>[a-zA-Z_]+)$', TriggerListView.as_view(),
    #     name='trigger_order_by'),
    # url(r'^th/trigger/$', TriggerListView.as_view(), name='home'),
    # ****************************************
    # * trigger
    # ****************************************
    # url(r'^th/trigger/delete/(?P<pk>\d+)$', TriggerDeleteView.as_view(), name='delete_trigger'),
    # url(r'^th/trigger/edit/(?P<pk>\d+)$', TriggerUpdateView.as_view(), name='edit_trigger'),
    # url(r'^th/trigger/editprovider/(?P<trigger_id>\d+)$', trigger_edit, {'edit_what': 'Provider'},
    #     name='edit_provider'),
    # url(r'^th/trigger/editconsumer/(?P<trigger_id>\d+)$', trigger_edit, {'edit_what': 'Consumer'},
    #    name='edit_consumer'),
    # url(r'^th/trigger/edit/thanks', TriggerEditedTemplateView.as_view(), name="trigger_edit_thanks"),
    # url(r'^th/trigger/delete/thanks', TriggerDeletedTemplateView.as_view(), name="trigger_delete_thanks"),
    # url(r'^th/trigger/onoff/(?P<trigger_id>\d+)$', trigger_on_off, name="trigger_on_off"),
    # url(r'^th/trigger/all/(?P<switch>(on|off))$', trigger_switch_all_to, name="trigger_switch_all_to"),
    # ****************************************
    # * service
    # ****************************************
    re_path(r'^th/service/$', UserServiceListView.as_view(), name='user_services'),
    re_path(r'^th/service/add/(?P<service_name>\w+)$', UserServiceCreateView.as_view(), name='add_service'),
    re_path(r'^th/service/edit/(?P<pk>\d+)$', UserServiceUpdateView.as_view(), name='edit_service'),
    re_path(r'^th/service/delete/(?P<pk>\d+)$', UserServiceDeleteView.as_view(), name='delete_service'),
    re_path(r'^th/service/renew/(?P<pk>\d+)$', renew_service, name="renew_service"),
    re_path(r'^th/service/delete/$', UserServiceDeleteView.as_view(), name='delete_service'),
    re_path(r'^th/service/onoff/(?P<user_service_id>\d+)/(?P<switch>(on|off))$', service_related_triggers_switch_to,
        name="service_related_triggers_switch_to"),
    # ****************************************
    # wizard
    # ****************************************
    re_path(r'^th/service/create/$',
        UserServiceWizard.as_view([ProviderForm,
                                   DummyForm,
                                   ConsumerForm,
                                   DummyForm,
                                   ServicesDescriptionForm]),
        name='create_service'),
    # every service will use django_th.views.finalcallback
    # and give the service_name value to use to
    # trigger the real callback
    re_path(r"^th/callbackevernote/$", finalcallback, {'service_name': 'ServiceEvernote', }, name="evernote_callback", ),
    re_path(r"^th/callbackgithub/$", finalcallback, {'service_name': 'ServiceGithub', }, name="github_callback", ),
    re_path(r"^th/callbackpocket/$", finalcallback, {'service_name': 'ServicePocket', }, name="pocket_callback", ),
    re_path(r"^th/callbackpushbullet/$", finalcallback, {'service_name': 'ServicePushbullet', },
        name="pushbullet_callback", ),
    re_path(r"^th/callbackreddit/$", finalcallback, {'service_name': 'ServiceReddit', }, name="reddit_callback", ),
    re_path(r"^th/callbacktodoist/$", finalcallback, {'service_name': 'ServiceTodoist', }, name="todoist_callback", ),
    re_path(r"^th/callbacktrello/$", finalcallback, {'service_name': 'ServiceTrello', }, name="trello_callback", ),
    re_path(r"^th/callbacktumblr/$", finalcallback, {'service_name': 'ServiceTumblr', }, name="tumblr_callback", ),
    re_path(r"^th/callbacktwitter/$", finalcallback, {'service_name': 'ServiceTwitter', }, name="twitter_callback", ),
    re_path(r"^th/callbackwallabag/$", finalcallback, {'service_name': 'ServiceWallabag', }, name="wallabag_callback", ),
    re_path(r"^th/callbackmastodon/$", finalcallback, {'service_name': 'ServiceMastodon', }, name="mastodon_callback", ),
    # url(r'^th/myfeeds/', include('th_services.th_rss.urls')),

    re_path(r'^th/api/taiga/webhook/', include('th_services.th_taiga.urls')),
    re_path(r'^th/api/slack/webhook/', include('th_services.th_slack.urls')),
    # dash
    re_path(r'^dashboard/', include('dash.urls', namespace='dash')),
    # API_REST
    re_path(r'^api/', include('api.urls')),
    re_path(r'^graphql', GraphQLView.as_view(graphiql=False)),
    # user guide
    re_path(r'^user-guide/', include('user_guide.urls')),
    # Feedback contact
    re_path(r'^feedback/', include('feedback.urls', namespace='feedback')),
    # Privacy policy
    re_path(r'^information/', include('information.urls', namespace='information'))
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
