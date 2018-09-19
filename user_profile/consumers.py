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

                await self.accept()
                await self.channel_layer.group_add(
                    profile_blog.group_name,
                    self.channel_name,
                )
            except Profile.DoesNotExist:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard("users-1", self.channel_name)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse a las notificaciones
    de un usuario
    """

    async def connect(self):
        self.user = self.scope["user"]
        await self.accept()

    async def receive_json(self, content):
        await self.send_json({"error": e.code})

    async def disconnect(self, code):
        pass
