from channels.generic.websockets import WebsocketConsumer
from user_profile.models import Profile
from .models import Photo, Video


class PhotoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        slug = kwargs.pop('slug', None)
        if not slug:
            return

        try:
            self.photo = Photo.objects.only('owner').get(slug__exact=slug)
        except Photo.DoesNotExist:
            return

        super(PhotoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.photo.group_name]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = Profile.objects.get(user_id=user.id)
            m = Profile.objects.get(user_id=self.photo.owner_id)
        except Profile.DoesNotExist:
            self.message.reply_channel.send({'close': True})
            return

        visibility = m.is_visible(n)

        if visibility and visibility != 'all':
            self.message.reply_channel({'close': True})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass


class VideoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        slug = kwargs.pop('slug', None)
        if not slug:
            return

        try:
            self.video = Video.objects.only('owner').get(slug__exact=slug)
        except Video.DoesNotExist:
            return

        super(VideoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.video.group_name]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = Profile.objects.get(user_id=user.id)
            m = Profile.objects.get(user_id=self.video.owner_id)
        except Profile.DoesNotExist:
            self.message.reply_channel.send({'close': True})
            return

        visibility = m.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'close': True})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass
