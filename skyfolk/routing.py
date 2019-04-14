from latest_news.consumers import MyFeedConsumer
from photologue.consumers import PhotoConsumer, VideoConsumer
from publications.consumers import PublicationConsumer
from publications_gallery.consumers import (
    PublicationPhotoConsumer,
    PublicationVideoConsumer,
)
from user_profile.consumers import BlogConsumer, NotificationConsumer
from user_groups.consumers import GroupConsumer, ThemeConsumer
from publications_groups.consumers import GroupPublicationConsumer
from photologue_groups.consumers import PhotoMediaGroupConsumer, VideoMediaGroupConsumer
from publications_gallery_groups.consumers import (
    PublicationGroupGalleryPhotoConsumer,
    PublicationGroupGalleryVideoConsumer,
)
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path


# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. WebSocket messages of all
# types have a 'path' attribute, so we're using that to route the socket.
# While this is under stream/ compared to the HTML page, we could have it on the
# same URL if we wanted; Daphne separates by protocol as it negotiates with a browser.

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("profile/<username>/stream/", BlogConsumer),
                    path("inicio/news/", MyFeedConsumer),
                    re_path(r"^.*/notification/$", NotificationConsumer),
                    re_path(
                        r"^publication/(?P<pubid>\d+)/stream/$", PublicationConsumer
                    ),
                    re_path(r"^group/(?P<groupname>[\w-]+)/stream/$", GroupConsumer),
                    re_path(
                        r"^group/publication/(?P<pk>\d+)/stream/$",
                        GroupPublicationConsumer,
                    ),
                    re_path(r"^groups/theme/(?P<slug>[\w-]+)/stream/$", ThemeConsumer),
                    re_path(
                        r"^multimedia/(?P<username>[\w-]+)/photo/(?P<slug>[\-\d\w]+)/stream/$",
                        PhotoConsumer,
                    ),
                    re_path(
                        r"^multimedia/(?P<username>[\w-]+)/video/(?P<slug>[\-\d\w]+)/stream/$",
                        VideoConsumer,
                    ),
                    re_path(
                        r"^photo/publication/(?P<pubid>\d+)/stream/$",
                        PublicationPhotoConsumer,
                    ),
                    re_path(
                        r"^video/publication/(?P<pubid>\d+)/stream/$",
                        PublicationVideoConsumer,
                    ),
                    re_path(
                        r"^group/photo/(?P<slug>[\w-]+)/stream/$",
                        PhotoMediaGroupConsumer,
                    ),
                    re_path(
                        r"^group/video/(?P<slug>[\w-]+)/stream/$",
                        VideoMediaGroupConsumer,
                    ),
                    re_path(
                        r"^group/multimedia/publication/detail/(?P<id>\d+)/stream/$",
                        PublicationGroupGalleryPhotoConsumer,
                    ),
                    re_path(
                        r"^group/multimedia/video/publication/detail/(?P<id>\d+)/stream/$",
                        PublicationGroupGalleryVideoConsumer,
                    ),
                ]
            )
        )
    }
)

# channel_routing = [
#     # Consumidor para el perfil del usuario
#     BlogConsumer.as_route(path=r'^/profile/(?P<username>[\w-]+)/stream/$'),
#     # channels en fotos
#     PhotoConsumer.as_route(path=r'^/multimedia/(?P<username>[\w-]+)/photo/(?P<slug>[\-\d\w]+)/stream/$'),
#     # channels en videos
#     VideoConsumer.as_route(path=r'^/multimedia/(?P<username>[\w-]+)/video/(?P<slug>[\-\d\w]+)/stream/$'),
#     # channels para notificaciones
#     NotificationConsumer.as_route(path=r'^.*/notification/$'),
#     # channels para inicio
#     MyFeedConsumer.as_route(path=r'^/inicio/news/$'),
#     # channels para conectarse a publication_detail
#     PublicationConsumer.as_route(path=r'^/publication/(?P<pubid>\d+)/stream/$'),
#     # channels para conectarse a publication_photo_detail
#     PublicationPhotoConsumer.as_route(path=r'^/photo/publication/(?P<pubid>\d+)/stream/$'),
#     # channels para conectarse a publication_video_detail
#     PublicationVideoConsumer.as_route(path=r'^/video/publication/(?P<pubid>\d+)/stream/$'),
#     # channels para conectarse a group
#     GroupConsumer.as_route(path=r'^/group/(?P<groupname>[\w-]+)/stream/$'),
#     # channels para conectarse a publication group detail
#     GroupPublicationConsumer.as_route(path=r'^/group/publication/(?P<pk>\d+)/stream/$'),
#     # channels para theme
#     ThemeConsumer.as_route(path=r'^/groups/theme/(?P<slug>[\w-]+)/stream/$'),
#     # photologue groups
#     # images
#     PhotoMediaGroupConsumer.as_route(path=r'^/group/photo/(?P<slug>[\w-]+)/stream/$'),
#     # videos
#     VideoMediaGroupConsumer.as_route(path=r'^/group/video/(?P<slug>[\w-]+)/stream/$'),
#     # photo publication detail
#     PublicationGroupGalleryPhotoConsumer.as_route(path=r'^/group/multimedia/publication/detail/(?P<id>\d+)/stream/$'),
#     # video publication detail
#     PublicationGroupGalleryVideoConsumer.as_route(
#         path=r'^/group/multimedia/video/publication/detail/(?P<id>\d+)/stream/$'),
#     # A default "http.request" route is always inserted by Django at the end of the routing list
#     # that routes all unmatched HTTP requests to the Django view system. If you want lower-level
#     # HTTP handling - e.g. long-polling - you can do it here and route by path, and let the rest
#     # fall through to normal views.
# ]
