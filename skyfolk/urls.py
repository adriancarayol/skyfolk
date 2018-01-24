from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.views.generic import TemplateView

from dash_services.forms.wizard import DummyForm, ProviderForm, ConsumerForm, ServicesDescriptionForm

from dash_services.views import TriggerListView, TriggerDeleteView, TriggerUpdateView, TriggerEditedTemplateView
from dash_services.views import TriggerDeletedTemplateView
from dash_services.views_fbv import logout_view, trigger_switch_all_to, trigger_edit, trigger_on_off
from dash_services.views_fbv import service_related_triggers_switch_to

from dash_services.views_userservices import UserServiceListView, UserServiceCreateView, UserServiceUpdateView
from dash_services.views_userservices import UserServiceDeleteView, renew_service
from dash_services.views_wizard import UserServiceWizard, finalcallback

from django_js_reverse.views import urls_js

admin.autodiscover()

# REST Framework
# router = routers.DefaultRouter()
# router.register(r'api/users', views.UserViewSet)
# router.register(r'api/groups', views.GroupViewSet)

urlpatterns = [
    # Importamos las URLS del resto de apps:
    url(r'^', include('landing.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),  # django-allauth
    # urls support
    url(r'^', include('support.urls', namespace="support"), name="support"),
    # urls user_profile
    url(r'^', include('user_profile.urls', namespace="user_profile"), name="user_profile"),
    # urls para grupos de usuarios
    url(r'^', include('user_groups.urls', namespace="user_groups"), name="user_groups"),
    # url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
    # {'document_root': settings.MEDIA_ROOT}),
    # url publications
    url(r'^', include('publications.urls', namespace="publications"), name="publications"),
    url(r'^', include('publications_groups.urls', namespace="publications_groups"),
        name="publications_groups"),
    url(r'^group/multimedia/', include('publications_gallery_groups.urls', namespace="publications_gallery_groups"),
        name="publications_gallery_groups"),
    # Publicaciones en imagenes de la galeria
    url(r'^', include('publications_gallery.urls', namespace="publications_gallery"), name="publications_gallery"),
    # url novedades e inicio
    url(r'^', include('latest_news.urls', namespace="latest_news"), name="news"),
    # url mensajes privados

    # About skyfolk
    url(r'^', include('about.urls')),
    # Recomendacion password para usuarios
    url(r'^tips/password/$', TemplateView.as_view(
        template_name='about/password_recommendation.html')),
    # Importamos las urls de REST Framework
    # url(r'^', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Urls para el modulo emoji
    url(r'^emoji/', include('emoji.urls', namespace="emoji")),
    # Django-avatar
    url(r'^', include('avatar.urls')),
    # notificaciones
    # url('^(?P<username>[\w-]+)/notifications/', include('notifications.urls',
    # namespace='notifications')),
    url('^inbox/notifications/', include('notifications.urls',
                                         namespace='notifications')),
    # django-photologue
    url(r'^', include('photologue.urls', namespace='photologue')),  # original photologue
    url(r'^group/', include('photologue_groups.urls', namespace='photologue_groups')),  # photologue groups
    url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),
    # django-dash URLs:
    # url(r'^dashboard/', include('dash.urls')),
    # url(r'^dash/contrib/plugins/rss-feed/', include('dash.contrib.plugins.rss_feed.urls')),
    # url(r'^contrib/', include('dash.contrib.apps.public_dashboard.urls')),
    # feedback
    url(r'^tellme/', include("tellme.urls")),
    # logros
    url(r'^badges/', include('badgify.urls')),
    url(r'^awards/', include('awards.urls')),
    # invitaciones
    url(r'^config/invitations/', include('invitations.urls', namespace='invitations')),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    # ****************************************
    # auth module
    # ****************************************
    url(r'^auth/', include('django.contrib.auth.urls')),
    # ****************************************
    # customized logout action
    # ****************************************
    url(r'^logout/$', logout_view, name='logout'),

    # ****************************************
    # trigger happy module
    # ****************************************
    url(r'^th/$', TriggerListView.as_view(), name='base'),
    url(r'^th/trigger/filter_by/(?P<trigger_filtered_by>[a-zA-Z]+)$', TriggerListView.as_view(),
        name='trigger_filter_by'),
    url(r'^th/trigger/order_by/(?P<trigger_ordered_by>[a-zA-Z_]+)$', TriggerListView.as_view(),
        name='trigger_order_by'),
    url(r'^th/trigger/$', TriggerListView.as_view(), name='home'),
    # ****************************************
    # * trigger
    # ****************************************
    url(r'^th/trigger/delete/(?P<pk>\d+)$', TriggerDeleteView.as_view(), name='delete_trigger'),
    url(r'^th/trigger/edit/(?P<pk>\d+)$', TriggerUpdateView.as_view(), name='edit_trigger'),
    url(r'^th/trigger/editprovider/(?P<trigger_id>\d+)$', trigger_edit, {'edit_what': 'Provider'},
        name='edit_provider'),
    url(r'^th/trigger/editconsumer/(?P<trigger_id>\d+)$', trigger_edit, {'edit_what': 'Consumer'},
        name='edit_consumer'),
    url(r'^th/trigger/edit/thanks', TriggerEditedTemplateView.as_view(), name="trigger_edit_thanks"),
    url(r'^th/trigger/delete/thanks', TriggerDeletedTemplateView.as_view(), name="trigger_delete_thanks"),
    url(r'^th/trigger/onoff/(?P<trigger_id>\d+)$', trigger_on_off, name="trigger_on_off"),
    url(r'^th/trigger/all/(?P<switch>(on|off))$', trigger_switch_all_to, name="trigger_switch_all_to"),
    # ****************************************
    # * service
    # ****************************************
    url(r'^th/service/$', UserServiceListView.as_view(), name='user_services'),
    url(r'^th/service/add/(?P<service_name>\w+)$', UserServiceCreateView.as_view(), name='add_service'),
    url(r'^th/service/edit/(?P<pk>\d+)$', UserServiceUpdateView.as_view(), name='edit_service'),
    url(r'^th/service/delete/(?P<pk>\d+)$', UserServiceDeleteView.as_view(), name='delete_service'),
    url(r'^th/service/renew/(?P<pk>\d+)$', renew_service, name="renew_service"),
    url(r'^th/service/delete/$', UserServiceDeleteView.as_view(), name='delete_service'),
    url(r'^th/service/onoff/(?P<user_service_id>\d+)/(?P<switch>(on|off))$', service_related_triggers_switch_to,
        name="service_related_triggers_switch_to"),
    # ****************************************
    # wizard
    # ****************************************
    url(r'^th/service/create/$',
        UserServiceWizard.as_view([ProviderForm,
                                   DummyForm,
                                   ConsumerForm,
                                   DummyForm,
                                   ServicesDescriptionForm]),
        name='create_service'),
    # every service will use django_th.views.finalcallback
    # and give the service_name value to use to
    # trigger the real callback
    url(r"^th/callbackevernote/$", finalcallback, {'service_name': 'ServiceEvernote', }, name="evernote_callback",),
    url(r"^th/callbackgithub/$", finalcallback, {'service_name': 'ServiceGithub', }, name="github_callback",),
    url(r"^th/callbackpocket/$", finalcallback, {'service_name': 'ServicePocket', }, name="pocket_callback",),
    url(r"^th/callbackpushbullet/$", finalcallback, {'service_name': 'ServicePushbullet', },
        name="pushbullet_callback",),
    url(r"^th/callbackreddit/$", finalcallback, {'service_name': 'ServiceReddit', }, name="reddit_callback",),
    url(r"^th/callbacktodoist/$", finalcallback, {'service_name': 'ServiceTodoist', }, name="todoist_callback",),
    url(r"^th/callbacktrello/$", finalcallback, {'service_name': 'ServiceTrello', }, name="trello_callback",),
    url(r"^th/callbacktumblr/$", finalcallback, {'service_name': 'ServiceTumblr', }, name="tumblr_callback",),
    url(r"^th/callbacktwitter/$", finalcallback, {'service_name': 'ServiceTwitter', }, name="twitter_callback",),
    url(r"^th/callbackwallabag/$", finalcallback, {'service_name': 'ServiceWallabag', }, name="wallabag_callback",),
    url(r"^th/callbackmastodon/$", finalcallback, {'service_name': 'ServiceMastodon', }, name="mastodon_callback",),
    url(r'^th/myfeeds/', include('th_rss.urls')),

    url(r'^th/api/taiga/webhook/', include('th_taiga.urls')),
    url(r'^th/api/slack/webhook/', include('th_slack.urls')),
    # dash
    url(r'^dashboard/', include('dash.urls')),
    url(r'^dash/contrib/plugins/rss-feed/',
                include('dash.contrib.plugins.rss_feed.urls')),
    url(r'^', include('dash.contrib.apps.public_dashboard.urls'))
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
