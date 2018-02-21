from channels.generic.websockets import WebsocketConsumer

from .models import PublicationGroup
from .utils import get_channel_name


class GroupPublicationConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        pubid = kwargs.get('pk', None)
        if not pubid:
            return

        try:
            publication_board_group = PublicationGroup.objects.get(id=pubid)
        except PublicationGroup.DoesNotExist:
            return

        self.group = publication_board_group.board_group

        super(GroupPublicationConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('pk', None)
        return [get_channel_name(pubid)]

    def connect(self, message, **kwargs):
        user = message.user

        if user.id != self.group.owner_id:
            if not self.group.is_public and not self.group.users.filter(id=user.id).exists():
                self.message.reply_channel({'close': True})
                return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        print(content)
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass
