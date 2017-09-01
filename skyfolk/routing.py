from channels import route

from photologue.consumers import PhotoConsumer
from user_profile.consumers import BlogConsumer, NotificationConsumer
from latest_news.consumers import MyFeedConsumer
from publications.consumers import PublicationConsumer
from publications_gallery.consumers import PublicationPhotoConsumer

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. WebSocket messages of all
# types have a 'path' attribute, so we're using that to route the socket.
# While this is under stream/ compared to the HTML page, we could have it on the
# same URL if we wanted; Daphne separates by protocol as it negotiates with a browser.
channel_routing = [
    # Consumidor para el perfil del usuario
    BlogConsumer.as_route(path=r'^/profile/(?P<username>[\w-]+)/stream/$'),
    # channels en fotos
    PhotoConsumer.as_route(path=r'^/photo/(?P<slug>[\-\d\w]+)/stream/$'),
    # channels para notificaciones
    NotificationConsumer.as_route(path=r'^.*/notification/$'),
    # channels para inicio
    MyFeedConsumer.as_route(path=r'^/inicio/news/$'),
    # channels para conectarse a publication_detail
    PublicationConsumer.as_route(path=r'^/publication/(?P<pubid>\d+)/stream/$'),
    # channels para conectarse a publication_photo_detail
    PublicationPhotoConsumer.as_route(path=r'^/publication_pdetail/(?P<pubid>\d+)/stream/$'),
    # A default "http.request" route is always inserted by Django at the end of the routing list
    # that routes all unmatched HTTP requests to the Django view system. If you want lower-level
    # HTTP handling - e.g. long-polling - you can do it here and route by path, and let the rest
    # fall through to normal views.
]
