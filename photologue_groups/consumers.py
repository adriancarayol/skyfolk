from channels.generic.websockets import WebsocketConsumer
from django.http import Http404
from user_profile.node_models import NodeProfile
from .models import PhotoGroup, VideoGroup


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
            raise Http404

        try:
            self.photo = PhotoGroup.objects.only('owner').get(slug__exact=slug)
        except PhotoGroup.DoesNotExist:
            raise Http404

        super(PhotoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.photo.group_name]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
            m = NodeProfile.nodes.get(user_id=self.photo.owner_id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})
            return

        visibility = m.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})

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
            raise Http404

        try:
            self.video = VideoGroup.objects.only('owner').get(slug__exact=slug)
        except VideoGroup.DoesNotExist:
            raise Http404

        super(VideoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.video.group_name]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
            m = NodeProfile.nodes.get(user_id=self.video.owner_id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})
            return

        visibility = m.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass