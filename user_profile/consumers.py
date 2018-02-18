from channels.generic.websockets import WebsocketConsumer
from django.http import Http404

from user_profile.models import Profile
from user_profile.node_models import NodeProfile


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
            return

        try:
            self.profile_blog = Profile.objects.get(user__username=username)
        except NodeProfile.DoesNotExist:
            return

        super(BlogConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.profile_blog.group_name]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            self.message.reply_channel.send({'close': True})
            return

        visibility = self.profile_blog.is_visible(n)

        if visibility and visibility != 'all':
            self.message.reply_channel({'close': True})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass


class NotificationConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse a las notificaciones
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def connection_groups(self, **kwargs):
        username = self.message.user.username
        if not username:
            return

        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return

        return [profile.notification_channel]

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass
