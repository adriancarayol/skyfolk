from channels.generic.websockets import WebsocketConsumer

from user_profile.models import NodeProfile
from .models import PublicationPhoto
from .utils import get_channel_name


class PublicationPhotoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        pubid = kwargs.get('pubid', None)
        if not pubid:
            raise Http404

        try:
            publication_board_owner = PublicationPhoto.objects.values_list('board_photo__owner_id', flat=True).get(id=pubid)
        except Publication.DoesNotExist:
            raise Http404

        try:
            self.board_owner = NodeProfile.nodes.get(user_id=publication_board_owner)
        except NodeProfile.DoesNotExist:
            raise Http404

        super(PublicationPhotoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('pubid', None)
        return [get_channel_name(pubid)]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})

        visibility = self.board_owner.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass