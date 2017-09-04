from channels.generic.websockets import WebsocketConsumer
from django.http import Http404

from .models import NodeProfile


class BlogConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        username = kwargs.pop('username', None)
        if not username:
            raise Http404

        try:
            self.profile_blog = NodeProfile.nodes.get(title=username)
        except NodeProfile.DoesNotExist:
            raise Http404

        super(BlogConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.profile_blog.group_name]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})

        visibility = self.profile_blog.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass

class NotificationConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def connection_groups(self, **kwargs):
        username = self.message.user.username
        if not username:
            raise Http404

        try:
            profile = NodeProfile.nodes.get(title=username)
        except NodeProfile.DoesNotExist:
            raise Http404

        return [profile.notification_channel]

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass