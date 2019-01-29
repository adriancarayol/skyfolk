from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from user_profile.models import Profile

@database_sync_to_async
def get_profile(user_id):
    profile = Profile.objects.get(user_id=user_id)
    return profile
    

class MyFeedConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
        else:
            try:
                profile = await get_profile(user.id)
                self.news_channels = profile.news_channel

                await self.channel_layer.group_add(
                    self.news_channels,
                    self.channel_name,
                )
                await self.accept()
            except Profile.DoesNotExist:
                await self.close()

    async def new_publication(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.news_channels, self.channel_name)
