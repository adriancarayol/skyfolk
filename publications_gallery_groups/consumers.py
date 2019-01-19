from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied
from user_profile.models import Profile
from .models import PublicationGroupMediaVideo, PublicationGroupMediaPhoto
from .utils import get_channel_name


class PublicationGroupGalleryPhotoConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_channel = None

    async def connect(self):
        user = self.scope["user"]
        pubid = self.scope['url_route']['kwargs']['id']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                publication_board_owner = PublicationGroupMediaPhoto.objects.select_related('board_photo__owner',
                                                                                            'board_photo__group').get(
                    id=pubid)

                group = publication_board_owner.board_photo.group

                if not group.is_public and user != group.owner_id:
                    if not user.user_groups.filter(id=group.id).exists():
                        raise PermissionDenied(
                            '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, pubid))

                board_owner = Profile.objects.get(user_id=publication_board_owner.board_photo.owner_id)
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
            except (PublicationGroupMediaPhoto.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.publication_channel, self.channel_name)


class PublicationGroupGalleryVideoConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_channel = None

    async def connect(self):
        user = self.scope["user"]
        pubid = self.scope['url_route']['kwargs']['id']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                publication_board_owner = PublicationGroupMediaVideo.objects.select_related('board_video__owner',
                                                                                            'board_video__group').get(
                    id=pubid)

                group = publication_board_owner.board_video.group

                if not group.is_public and user != group.owner_id:
                    if not user.user_groups.filter(id=group.id).exists():
                        raise PermissionDenied(
                            '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, pubid))

                board_owner = Profile.objects.get(user_id=publication_board_owner.board_video.owner_id)
                n = Profile.objects.get(user_id=user.id)

                visibility = board_owner.is_visible(n)

                if visibility and visibility != 'all':
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, pubid))

                self.publication_channel = "group-video-pub-{}".format(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel,
                    self.channel_name,
                )
                await self.accept()
            except (PublicationGroupMediaVideo.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.publication_channel, self.channel_name)