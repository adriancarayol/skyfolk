from channels.generic.websockets import WebsocketConsumer

from user_profile.node_models import NodeProfile
from .models import PublicationGroup
from .utils import get_channel_name
from user_groups.models import UserGroups
from user_groups.node_models import NodeGroup


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
            publication_board_group = PublicationGroup.objects.values_list('board_group__id', flat=True).get(
                id=pubid)
        except PublicationGroup.DoesNotExist:
            return

        try:
            self.group = NodeGroup.nodes.get(group_id=publication_board_group)
        except NodeProfile.DoesNotExist:
            return

        super(GroupPublicationConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('pk', None)
        return [get_channel_name(pubid)]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'close': True})
            return

        try:
            g = UserGroups.objects.get(group_ptr_id=self.group.group_id)
        except UserGroups.DoesNotExist:
            self.message.reply_channel.send({'close': True})
            return

        if not g.is_public and not g.members.is_connected(n):
            self.message.reply_channel({'close': True})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        print(content)
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass
