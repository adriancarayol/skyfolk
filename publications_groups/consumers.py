from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied
from .models import PublicationGroup
from .utils import get_channel_name
from channels.db import database_sync_to_async


@database_sync_to_async
def get_publication_group(pubid):
    publication = PublicationGroup.objects.select_related("board_group").get(id=pubid)
    return publication


@database_sync_to_async
def exists_user_in_group(group, user_id):
    return group.users.filter(id=user_id).exists()


class GroupPublicationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_channel = None

    async def connect(self):
        user = self.scope["user"]
        pubid = self.scope["url_route"]["kwargs"]["pk"]

        if user.is_anonymous:
            await self.close()
        else:
            try:
                publication_board_group = await get_publication_group(pubid)
                group = publication_board_group.board_group
                exists_in_group = await exists_user_in_group(group, user.id)

                if user.id != group.owner_id:
                    if not group.is_public and not exists_in_group:
                        raise PermissionDenied(
                            "{} no tiene permisos para conectarse a esta channel: {}".fornmat(
                                user, pubid
                            )
                        )

                self.publication_channel = get_channel_name(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel, self.channel_name
                )
                await self.accept()
            except PublicationGroup.DoesNotExist as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.publication_channel, self.channel_name
        )
