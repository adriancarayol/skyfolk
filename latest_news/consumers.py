from channels.generic.websockets import WebsocketConsumer

from user_profile.models import NodeProfile


class MyFeedConsumer(WebsocketConsumer):
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

        return [profile.news_channel]

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass