from channels.generic.websocket import AsyncJsonWebsocketConsumer
from user_profile.models import Profile
from .models import Photo, Video
from django.core.exceptions import PermissionDenied


class PhotoConsumer(AsyncJsonWebsocketConsumer):
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
                photo = Photo.objects.only('owner').get(slug__exact=slug)

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
            except (Photo.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.photo_channel, self.channel_name)


class VideoConsumer(AsyncJsonWebsocketConsumer):
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
                video = Video.objects.only('owner').get(slug__exact=slug)

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
            except (Video.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.video_channel, self.channel_name)
