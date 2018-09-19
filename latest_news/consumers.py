from channels.generic.websocket import AsyncJsonWebsocketConsumer

from user_profile.models import Profile


class MyFeedConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    async def connect(self):
        self.user = self.scope["user"]
        print('CONECTADO...: {}'.format(self.user))
        await self.accept()

    async def receive_json(self, content):
        await self.send_json({"error": e.code})

    async def disconnect(self, code):
        pass