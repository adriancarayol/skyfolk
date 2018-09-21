from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
from django.http import Http404
from channels.layers import get_channel_layer
from user_profile.models import Profile
from user_profile.node_models import NodeProfile

channel_layer = get_channel_layer()


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
                profile_blog = Profile.objects.get(user__username=profile_username)
                user_profile = Profile.objects.get(user__username=self.user.username)

                visibility = profile_blog.is_visible(user_profile)

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
                profile = Profile.objects.get(user__username=self.user.username)
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
