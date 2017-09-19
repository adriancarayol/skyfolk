from channels.generic.websockets import WebsocketConsumer
from django.http import Http404

from user_profile.node_models import NodeProfile
from .models import UserGroups, GroupTheme
from user_groups.node_models import NodeGroup


class GroupConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        groupname = kwargs.pop('groupname', None)
        if not groupname:
            raise Http404

        try:
            self.group_profile = UserGroups.objects.get(slug=groupname)
        except UserGroups.DoesNotExist:
            raise Http404

        super(GroupConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.group_profile.group_channel]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            raise Http404

        try:
            g = NodeGroup.nodes.get(group_id=self.group_profile.group_ptr_id)
        except NodeGroup.DoesNotExist:
            raise Http404

        if not self.group_profile.is_public and not g.members.is_connected(n):
            self.message.reply_channel.send({'accept': False})

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass


class ThemeConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        slug = kwargs.pop('slug', None)
        if not slug:
            raise Http404

        try:
            self.theme = GroupTheme.objects.select_related('board_group').get(slug=slug)
        except UserGroups.DoesNotExist:
            raise Http404

        super(ThemeConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.theme.theme_channel]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            group = UserGroups.objects.get(id=self.theme.board_group_id)
        except UserGroups.DoesNotExist:
            raise Http404

        if not group.is_public and not user.groups.filter(id=self.theme.board_group_id).exists():
            self.message.reply_channel.send({'accept': False})

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass
