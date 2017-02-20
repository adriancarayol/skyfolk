from channels import route

#from notifications.consumers import ws_connect
from photologue.consumers import connect_photo, disconnect_photo
from user_profile.consumers import connect_blog, disconnect_blog, ws_connect
from latest_news.consumers import ws_connect_news, disconnect_news

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. WebSocket messages of all
# types have a 'path' attribute, so we're using that to route the socket.
# While this is under stream/ compared to the HTML page, we could have it on the
# same URL if we wanted; Daphne separates by protocol as it negotiates with a browser.
channel_routing = [
    # Called when incoming WebSockets connect
    route("websocket.connect", connect_blog, path=r'^/profile/(?P<username>[\w-]+)/stream/$'),
    # Called when the client closes the socket
    route("websocket.disconnect", disconnect_blog, path=r'^/profile/(?P<username>[\w-]+)/stream/$'),
    # channels en fotos
    route("websocket.connect", connect_photo, path=r'^/photo/(?P<slug>[\-\d\w]+)/stream/$'),
    route("websocket.disconnect", disconnect_photo, path=r'^/photo/(?P<slug>[\-\d\w]+)/stream/$'),
    # channels para notificaciones
    route("websocket.connect", ws_connect, path=r'^.*/notification/$'),
    # channels para inicio (conectar)
    route("websocket.connect", ws_connect_news, path=r'^/inicio/news/$'),
    # channels para inicio (desconectar)
    route("websocket.disconnect", disconnect_news, path=r'^/inicio/news/$'),
    # A default "http.request" route is always inserted by Django at the end of the routing list
    # that routes all unmatched HTTP requests to the Django view system. If you want lower-level
    # HTTP handling - e.g. long-polling - you can do it here and route by path, and let the rest
    # fall through to normal views.
]
