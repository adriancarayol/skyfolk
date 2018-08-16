from channels.generic.websockets import WebsocketConsumer

from user_profile.models import Profile
from .models import Publication
from .utils import get_channel_name


class PublicationConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        pubid = kwargs.get('pubid', None)
        if not pubid:
            return

        try:
            publication_board_owner = Publication.objects.values_list('board_owner__id', flat=True).get(id=pubid)
        except Publication.DoesNotExist:
            return

        try:
            self.board_owner = Profile.objects.get(user_id=publication_board_owner)
        except Profile.DoesNotExist:
            return

        super(PublicationConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('pubid', None)
        return [get_channel_name(pubid)]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            self.message.reply_channel.send({'close': True})
            return

        visibility = self.board_owner.is_visible(n)

        if visibility and visibility != 'all':
            self.message.reply_channel({'close': True})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass