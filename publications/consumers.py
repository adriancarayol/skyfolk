import json
import logging

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from .utils import get_channel_name
from .models import Publication
from user_profile.models import NodeProfile


@channel_session_user_from_http
def connect_publication(message, pubid):
    user = message.user
    try:
        publication_board_owner = Publication.objects.values_list('board_owner__id', flat=True).get(id=pubid)
        print(publication_board_owner)
        n = NodeProfile.nodes.get(user_id=publication_board_owner)
        m = NodeProfile.nodes.get(user_id=user.id)
        visibility = n.is_visible(m)
        if visibility and visibility != 'all':
            logging.warning('User: {} no puede conectarse al socket de: profile: {}'.format(user.username, username))
            message.reply_channel.send({"accept": False})
            return
    except Publication.DoesNotExist:
        message.reply_channel.send({
            'text': json.dumps({'error': 'bad_slug'}),
            'close': True,
        })
        return
    message.reply_channel.send({'accept': True})
    Group(get_channel_name(pubid)).add(message.reply_channel)


@channel_session_user
def disconnect_publication(message, pubid):
    """
    Removes the user from the liveblog group when they disconnect.

    Channels will auto-cleanup eventually, but it can take a while, and having old
    entries cluttering up your group will reduce performance.
    """
    try:
        publication_board_owner = Publication.objects.values_list('board_owner__id', flat=True).get(id=pubid)
    except Publication.DoesNotExist:
        # This is the disconnect message, so the socket is already gone; we can't
        # send an error back. Instead, we just return from the consumer.
        return
    # It's called .discard() because if the reply channel is already there it
    # won't fail - just like the set() type.
    Group(get_channel_name(pubid)).discard(message.reply_channel)

