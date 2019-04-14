from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import PermissionDenied
from user_profile.models import Profile
from .models import PublicationGroupMediaVideo, PublicationGroupMediaPhoto
from .utils import get_channel_name
from channels.db import database_sync_to_async


@database_sync_to_async
def get_profile(user_id):
    profile = Profile.objects.get(user_id=user_id)
    return profile


@database_sync_to_async
def get_board_owner(pub_id):
    return PublicationGroupMediaPhoto.objects.select_related(
        "board_photo__owner", "board_photo__group"
    ).get(id=pub_id)


@database_sync_to_async
def exists_group_in_user(user, group_id):
    return user.user_groups.filter(id=group_id).exists()


@database_sync_to_async
def is_visible(from_profile, to_profile):
    return from_profile.is_visible(to_profile)


class PublicationGroupGalleryPhotoConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_channel = None

    async def connect(self):
        user = self.scope["user"]
        pubid = self.scope["url_route"]["kwargs"]["id"]

        if user.is_anonymous:
            await self.close()
        else:
            try:
                publication_board_owner = await get_board_owner(pubid)
                group = publication_board_owner.board_photo.group

                exists_in_group = await exists_group_in_user(user, group.id)

                if not group.is_public and user != group.owner_id:
                    if not exists_in_group:
                        raise PermissionDenied(
                            "{} no tiene permisos para conectarse a esta channel: {}".fornmat(
                                user, pubid
                            )
                        )

                board_owner = await get_profile(
                    publication_board_owner.board_photo.owner_id
                )
                n = await get_profile(user.id)

                visibility = await is_visible(board_owner, n)

                if visibility and visibility != "all":
                    raise PermissionDenied(
                        "{} no tiene permisos para conectarse a esta channel: {}".fornmat(
                            user, pubid
                        )
                    )

                self.publication_channel = get_channel_name(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel, self.channel_name
                )
                await self.accept()
            except (PublicationGroupMediaPhoto.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.publication_channel, self.channel_name
        )


@database_sync_to_async
def get_board_owner_video(pub_id):
    return PublicationGroupMediaVideo.objects.select_related(
        "board_video__owner", "board_video__group"
    ).get(id=pub_id)


class PublicationGroupGalleryVideoConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumidor para conectarse al perfil
    de un usuario
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publication_channel = None

    async def connect(self):
        user = self.scope["user"]
        pubid = self.scope["url_route"]["kwargs"]["id"]

        if user.is_anonymous:
            await self.close()
        else:
            try:
                publication_board_owner = await get_board_owner_video(pubid)

                group = publication_board_owner.board_video.group

                exists_in_group = await exists_group_in_user(user, group.id)

                if not group.is_public and user != group.owner_id:
                    if not exists_in_group:
                        raise PermissionDenied(
                            "{} no tiene permisos para conectarse a esta channel: {}".fornmat(
                                user, pubid
                            )
                        )

                board_owner = await get_profile(
                    publication_board_owner.board_video.owner_id
                )
                n = await get_profile(user.id)

                visibility = await is_visible(board_owner, n)

                if visibility and visibility != "all":
                    raise PermissionDenied(
                        "{} no tiene permisos para conectarse a esta channel: {}".fornmat(
                            user, pubid
                        )
                    )

                self.publication_channel = "group-video-pub-{}".format(pubid)

                await self.channel_layer.group_add(
                    self.publication_channel, self.channel_name
                )
                await self.accept()
            except (PublicationGroupMediaVideo.DoesNotExist, Profile.DoesNotExist) as e:
                await self.close()
            except PermissionDenied:
                await self.close()

    async def new_publication(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send_json(message)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.publication_channel, self.channel_name
        )
