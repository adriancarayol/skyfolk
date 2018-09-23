from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied
from .models import UserGroups, GroupTheme


class GroupConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_profile_channel = None

    async def connect(self):
        user = self.scope["user"]

        groupname = self.scope['url_route']['kwargs']['groupname']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                group_profile = UserGroups.objects.get(slug=groupname)

                if not group_profile.is_public and not group_profile.users.filter(id=user.id).exists():
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.format(user, groupname))

                self.group_profile_channel = group_profile.group_channel

                await self.accept()
                await self.channel_layer.group_add(
                    self.group_profile_channel,
                    self.channel_name,
                )
            except Profile.DoesNotExist:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_profile_channel, self.channel_name)


class ThemeConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_channel = None

    async def connect(self):
        user = self.scope["user"]

        slug = self.scope['url_route']['kwargs']['slug']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                theme = GroupTheme.objects.select_related('board_group').get(slug=slug)
                group_profile = UserGroups.objects.get(id=theme.board_group_id)

                if not group_profile.is_public and not user.user_groups.filter(id=theme.board_group_id).exists():
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.format(user, groupname))

                self.theme_channel = theme.theme_channel

                await self.accept()
                await self.channel_layer.group_add(
                    self.theme_channel,
                    self.channel_name,
                )
            except Profile.DoesNotExist:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.theme_channel, self.channel_name)
