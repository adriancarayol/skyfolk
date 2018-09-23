from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied
from django.http import Http404
from user_profile.models import Profile
from user_profile.node_models import NodeProfile
from .models import PublicationPhoto, PublicationVideo
from .utils import get_channel_name


class PublicationPhotoConsumer(AsyncJsonWebsocketConsumer):
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
                publication_board_owner = PublicationPhoto.objects.values_list('board_photo__owner_id', flat=True).get(
                    id=pubid)
                board_owner = Profile.objects.get(user_id=publication_board_owner)
                n = Profile.objects.get(user_id=user.id)

                visibility = board_owner.is_visible(n)

                if visibility and visibility != 'all':
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, pubid))

                self.publication_channel = get_channel_name(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel,
                    self.channel_name,
                )
                await self.accept()
            except (PublicationPhoto.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.publication_channel, self.channel_name)


class PublicationVideoConsumer(AsyncJsonWebsocketConsumer):
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
                publication_board_owner = PublicationVideo.objects.values_list('board_video__owner_id', flat=True).get(
                    id=pubid)
                board_owner = Profile.objects.get(user_id=publication_board_owner)
                n = Profile.objects.get(user_id=user.id)

                visibility = board_owner.is_visible(n)

                if visibility and visibility != 'all':
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, pubid))

                self.publication_channel = "video-pub-{}".format(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel,
                    self.channel_name,
                )
                await self.accept()
            except (PublicationVideo.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.publication_channel, self.channel_name)
