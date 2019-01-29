from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.http import Http404
from channels.layers import get_channel_layer
from user_profile.models import Profile
from channels.db import database_sync_to_async


channel_layer = get_channel_layer()

@database_sync_to_async
def get_profile(username):
    profile = Profile.objects.get(user__username=username)
    return profile

@database_sync_to_async
def is_visible(from_profile, to_profile):
    return from_profile.is_visible(to_profile)

class BlogConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    async def connect(self):
        self.user = self.scope["user"]

        profile_username = self.scope['url_route']['kwargs']['username']

        if self.user.is_anonymous:
            await self.close()
        else:
            try:
                profile_blog = await get_profile(profile_username)
                user_profile = await get_profile(self.user.username)

                visibility = await is_visible(profile_blog, user_profile)

                if visibility and visibility != 'all':
                    await self.close()
                    return

                self.profile_blog = profile_blog.group_name

                await self.accept()
                await self.channel_layer.group_add(
                    self.profile_blog,
                    self.channel_name,
                )
            except Profile.DoesNotExist:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.profile_blog, self.channel_name)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse a las notificaciones
    de un usuario
    """

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            try:
                profile = await get_profile(self.user.username)
                self.notification_channel = profile.notification_channel
                await self.channel_layer.group_add(
                    self.notification_channel,
                    self.channel_name,
                )
                await self.accept()
            except Profile.DoesNotExist:
                await self.close()

    async def new_notification(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.notification_channel, self.channel_name)
