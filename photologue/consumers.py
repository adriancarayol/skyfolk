from channels.generic.websocket import AsyncJsonWebsocketConsumer
from user_profile.models import Profile
from .models import Photo, Video
from django.core.exceptions import PermissionDenied
from channels.db import database_sync_to_async


@database_sync_to_async
def get_profile(user_id):
    profile = Profile.objects.get(user_id=user_id)
    return profile

@database_sync_to_async
def get_photo(slug):
    photo = Photo.objects.select_related('owner').get(slug__exact=slug)
    return photo

@database_sync_to_async
def is_visible(from_profile, to_profile):
    return from_profile.is_visible(to_profile)

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
                photo = await get_photo(slug)

                n = await get_profile(user.id)
                m = await get_profile(photo.owner_id)

                visibility = await is_visible(m, n)

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


@database_sync_to_async
def get_video(slug):
    video = Video.objects.select_related('owner').get(slug__exact=slug)
    return video

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
                video = await get_video(slug)

                n = await get_profile(user.id)
                m = await get_profile(video.owner_id)

                visibility = await is_visible(m, n)

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
