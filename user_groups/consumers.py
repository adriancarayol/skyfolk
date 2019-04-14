from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied
from .models import UserGroups, GroupTheme
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_group(groupname):
    group_profile = UserGroups.objects.get(slug=groupname)
    return group_profile


@database_sync_to_async
def exists_user_in_group(group_profile, user_id):
    return group_profile.users.filter(id=user_id).exists()


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

        groupname = self.scope["url_route"]["kwargs"]["groupname"]

        if user.is_anonymous:
            await self.close()
        else:
            try:
                group_profile = await get_user_group(groupname)
                exists_in_group = await exists_user_in_group(group_profile, user.id)

                if not group_profile.is_public and not exists_in_group:
                    raise PermissionDenied(
                        "{} no tiene permisos para conectarse a esta channel: {}".format(
                            user, groupname
                        )
                    )

                self.group_profile_channel = group_profile.group_channel

                await self.accept()
                await self.channel_layer.group_add(
                    self.group_profile_channel, self.channel_name
                )
            except UserGroups.DoesNotExist:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_profile_channel, self.channel_name
        )


@database_sync_to_async
def get_group_theme(slug):
    theme = GroupTheme.objects.select_related("board_group").get(slug=slug)
    return theme


@database_sync_to_async
def get_user_group_by_id(group_id):
    user_group = UserGroups.objects.get(id=group_id)
    return user_group


@database_sync_to_async
def exists_user_group_in_user(user, user_group_id):
    return user.user_groups.filter(id=user_group_id).exists()


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

        slug = self.scope["url_route"]["kwargs"]["slug"]

        if user.is_anonymous:
            await self.close()
        else:
            try:
                theme = await get_group_theme(slug)
                group_profile = await get_user_group_by_id(theme.board_group_id)

                exists_user_group_in_user_profile = await exists_user_group_in_user(
                    user, theme.board_group_id
                )

                if (
                    not group_profile.is_public
                    and not exists_user_group_in_user_profile
                ):
                    raise PermissionDenied(
                        "{} no tiene permisos para conectarse a esta channel: {}".format(
                            user, theme
                        )
                    )

                self.theme_channel = theme.theme_channel

                await self.accept()
                await self.channel_layer.group_add(
                    self.theme_channel, self.channel_name
                )
            except (UserGroups.DoesNotExist, GroupTheme.DoesNotExist) as ex:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.theme_channel, self.channel_name)
