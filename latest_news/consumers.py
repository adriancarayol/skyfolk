from channels.generic.websockets import WebsocketConsumer

from user_profile.models import Profile


class MyFeedConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def connection_groups(self, **kwargs):
        id = self.message.user.id

        if not id:
            return

        try:
            profile = Profile.objects.get(user_id=id)
        except Profile.DoesNotExist:
            return

        return [profile.news_channel]

    def connect(self, message, **kwargs):
        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass