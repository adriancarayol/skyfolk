from channels.generic.websockets import WebsocketConsumer
from django.http import Http404
from user_profile.node_models import NodeProfile
from .models import PublicationPhoto, PublicationVideo
from .utils import get_channel_name


class PublicationPhotoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        pubid = kwargs.get('pubid', None)
        if not pubid:
            raise Http404

        try:
            publication_board_owner = PublicationPhoto.objects.values_list('board_photo__owner_id', flat=True).get(id=pubid)
        except PublicationPhoto.DoesNotExist:
            raise Http404

        try:
            self.board_owner = NodeProfile.nodes.get(user_id=publication_board_owner)
        except NodeProfile.DoesNotExist:
            raise Http404

        super(PublicationPhotoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('pubid', None)
        return [get_channel_name(pubid)]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})

        visibility = self.board_owner.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass


class PublicationVideoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        print('xdxdxdxdxdxd')

        pubid = kwargs.get('pubid', None)
        if not pubid:
            raise Http404

        try:
            publication_board_owner = PublicationVideo.objects.values_list('board_video__owner_id', flat=True).get(id=pubid)
        except PublicationVideo.DoesNotExist:
            raise Http404

        try:
            self.board_owner = NodeProfile.nodes.get(user_id=publication_board_owner)
        except NodeProfile.DoesNotExist:
            raise Http404

        super(PublicationVideoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('pubid', None)
        return ["video-pub-{}".format(pubid)]

    def connect(self, message, **kwargs):
        user = message.user
        try:
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})
            return

        visibility = self.board_owner.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        print(content)
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass