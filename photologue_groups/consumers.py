from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.http import Http404
from django.core.exceptions import PermissionDenied
from user_profile.models import Profile
from .models import PhotoGroup, VideoGroup


class PhotoMediaGroupConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_channel = None

    async def connect(self):
        user = self.scope["user"]
        slug = self.scope['url_route']['kwargs']['slug']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                photo = PhotoGroup.objects.select_related('owner', 'group').get(slug__exact=slug)
                group = photo.group

                if not group.is_public and user != group.owner_id:
                    if not user.user_groups.filter(id=group.id).exists():
                        raise PermissionDenied(
                            '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, slug))

                n = Profile.objects.get(user_id=user.id)
                m = Profile.objects.get(user_id=photo.owner_id)

                visibility = m.is_visible(n)

                if visibility and visibility != 'all':
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, slug))

                self.photo_channel = photo.group_name

                await self.channel_layer.group_add(
                    self.photo_channel,
                    self.channel_name,
                )
                await self.accept()
            except (PhotoGroup.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.photo_channel, self.channel_name)


class VideoMediaGroupConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_channel = None

    async def connect(self):
        user = self.scope["user"]
        slug = self.scope['url_route']['kwargs']['slug']

        if user.is_anonymous:
            await self.close()
        else:
            try:
                video = VideoGroup.objects.select_related('owner', 'group').get(slug__exact=slug)

                n = Profile.objects.get(user_id=user.id)
                m = Profile.objects.get(user_id=video.owner_id)

                visibility = m.is_visible(n)

                if visibility and visibility != 'all':
                    raise PermissionDenied(
                        '{} no tiene permisos para conectarse a esta channel: {}'.fornmat(user, slug))

                self.video_channel = video.group_name

                await self.channel_layer.group_add(
                    self.video_channel,
                    self.channel_name,
                )
                await self.accept()
            except (VideoGroup.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.video_channel, self.channel_name)
