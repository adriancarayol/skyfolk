from channels.generic.websocket import AsyncJsonWebsocketConsumer

from user_profile.models import Profile


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
                profile = Profile.objects.get(user_id=user.id)
                self.news_channels = profile.news_channel

                await self.channel_layer.group_add(
                    self.news_channels,
                    self.channel_name,
                )
                await self.accept()
            except Profile.DoesNotExist:
                await self.close()

    async def receive_json(self, content):
        await self.send_json({"error": e.code})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.news_channels, self.channel_name)
