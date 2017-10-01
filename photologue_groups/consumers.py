from channels.generic.websockets import WebsocketConsumer
from django.http import Http404

from user_profile.node_models import NodeProfile
from .models import PhotoGroup, VideoGroup


class PhotoMediaGroupConsumer(WebsocketConsumer):
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
            self.photo = PhotoGroup.objects.select_related('owner', 'group').get(slug__exact=slug)
        except PhotoGroup.DoesNotExist:
            raise Http404

        super(PhotoMediaGroupConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.photo.group_name]

    def connect(self, message, **kwargs):
        user = message.user

        group = self.photo.group

        if not group.is_public and user != group.owner_id:
            if not user.groups.filter(id=group.group_ptr_id).exists():
                self.message.reply_channel({'accept': False})

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


class VideoMediaGroupConsumer(WebsocketConsumer):
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
            self.video = VideoGroup.objects.select_related('owner', 'group').get(slug__exact=slug)
        except VideoGroup.DoesNotExist:
            raise Http404

        super(VideoMediaGroupConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        return [self.video.group_name]

    def connect(self, message, **kwargs):
        user = message.user

        group = self.video.group

        if not group.is_public and user != group.owner_id:
            if not user.groups.filter(id=group.group_ptr_id).exists():
                self.message.reply_channel({'accept': False})

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