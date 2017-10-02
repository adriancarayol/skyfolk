from channels.generic.websockets import WebsocketConsumer
from django.http import Http404
from user_profile.node_models import NodeProfile
from .models import PublicationGroupMediaVideo, PublicationGroupMediaPhoto
from .utils import get_channel_name


class PublicationGroupGalleryPhotoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        pubid = kwargs.get('id', None)
        if not pubid:
            raise Http404

        try:
            self.publication = PublicationGroupMediaPhoto.objects.select_related('board_photo__owner', 'board_photo__group').get(id=pubid)
        except PublicationGroupMediaPhoto.DoesNotExist:
            raise Http404

        super(PublicationGroupGalleryPhotoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('id', None)
        return [get_channel_name(pubid)]

    def connect(self, message, **kwargs):
        user = message.user

        group = self.publication.board_photo.group

        if not group.is_public and user != group.owner_id:
            if not user.groups.filter(id=group.group_ptr_id).exists():
                self.message.reply_channel({'accept': False})
                return

        try:
            n = NodeProfile.nodes.get(user_id=user.id)
            board_owner = NodeProfile.nodes.get(user_id=self.publication.board_photo.owner_id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})
            return

        visibility = board_owner.is_visible(n)
        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass


class PublicationGroupGalleryVideoConsumer(WebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """
    http_user = True
    strict_ordering = False

    def __init__(self, message, **kwargs):
        pubid = kwargs.get('id', None)
        if not pubid:
            raise Http404

        try:
            self.publication = PublicationGroupMediaVideo.objects.select_related('board_video__owner',
                                                                                 'board_video__group').get(id=pubid)
        except PublicationGroupMediaVideo.DoesNotExist:
            raise Http404


        super(PublicationGroupGalleryVideoConsumer, self).__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        pubid = kwargs.get('id', None)
        return ["group-video-pub-{}".format(pubid)]

    def connect(self, message, **kwargs):
        user = message.user

        group = self.publication.board_video.group

        if not group.is_public and user != group.owner_id:
            if not user.groups.filter(id=group.group_ptr_id).exists():
                self.message.reply_channel({'accept': False})
                return

        try:
            n = NodeProfile.nodes.get(user_id=user.id)
            board_owner = NodeProfile.nodes.get(user_id=self.publication.board_video.owner_id)
        except NodeProfile.DoesNotExist:
            self.message.reply_channel.send({'accept': False})
            return

        visibility = board_owner.is_visible(n)

        if visibility and visibility != 'all':
            self.message.reply_channel({'accept': False})
            return

        self.message.reply_channel.send({'accept': True})

    def receive(self, content, **kwargs):
        print(content)
        self.send(content)

    def disconnect(self, message, **kwargs):
        pass