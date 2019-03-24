from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied

from user_profile.models import Profile
from .models import Publication
from .utils import get_channel_name


@database_sync_to_async
def get_profile(user_id):
    profile = Profile.objects.get(user_id=user_id)
    return profile

@database_sync_to_async
def get_board_owner(pub_id):
    return Publication.objects.values_list('board_owner__id', flat=True).get(id=pub_id)

@database_sync_to_async
def is_visible(from_profile, to_profile):
    return from_profile.is_visible(to_profile)

class PublicationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_channel = None

    async def connect(self):
        user = self.scope["user"]
        pubid = self.scope['url_route']['kwargs']['pubid']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                publication_board_owner = await get_board_owner(pubid)
                board_owner = await get_profile(publication_board_owner)
                n = await get_profile(user.id)

                visibility = await is_visible(board_owner, n)

                if visibility and visibility != 'all':
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, pubid))

                self.publication_channel = get_channel_name(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel,
                    self.channel_name,
                )
                await self.accept()
            except (Publication.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.publication_channel, self.channel_name)
