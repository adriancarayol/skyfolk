import json
import logging

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from .models import NodeProfile


# The "slug" keyword argument here comes from the regex capture group in
#
@channel_session_user_from_http
def connect_blog(message, username):
    """
    When the user opens a WebSocket to a liveblog stream, adds them to the
    group for that stream so they receive new post notifications.

    The notifications are actually sent in the Post model on save.
    """
    # Try to fetch the liveblog by slug; if that fails, close the socket.
    user = message.user

    try:
        profile_blog = NodeProfile.nodes.get(title=username)
        n = NodeProfile.nodes.get(user_id=user.id)
        visibility = profile_blog.is_visible(n)
        if visibility and visibility != 'all':
            logging.warning('User: {} no puede conectarse al socket de: profile: {}'.format(user.username, username))
            message.reply_channel.send({"accept": False})
            return
    except NodeProfile.DoesNotExist:
        # You can see what messages back to a WebSocket look like in the spec:
        # http://channels.readthedocs.org/en/latest/asgi.html#send-close
        # Here, we send "close" to make Daphne close off the socket, and some
        # error text for the client.
        message.reply_channel.send({
            # WebSockets send either a text or binary payload each frame.
            # We do JSON over the text portion.
            "text": json.dumps({"error": "bad_slug"}),
            "close": True,
        })
        return
    # Each different client has a different "reply_channel", which is how you
    # send information back to them. We can add all the different reply channels
    # to a single Group, and then when we send to the group, they'll all get the
    # same message.
    message.reply_channel.send({"accept": True})
    Group(profile_blog.group_name).add(message.reply_channel)


@channel_session_user
def disconnect_blog(message, username):
    """
    Removes the user from the liveblog group when they disconnect.

    Channels will auto-cleanup eventually, but it can take a while, and having old
    entries cluttering up your group will reduce performance.
    """
    try:
        profile_blog = NodeProfile.nodes.get(title=username)
    except NodeProfile.DoesNotExist:
        # This is the disconnect message, so the socket is already gone; we can't
        # send an error back. Instead, we just return from the consumer.
        return
    # It's called .discard() because if the reply channel is already there it
    # won't fail - just like the set() type.
    Group(profile_blog.group_name).discard(message.reply_channel)


# Para recibir notificaciones privadas
@channel_session_user_from_http
def ws_connect(message):
    username = message.user.username
    try:
        profile = NodeProfile.nodes.get(title=username)
    except NodeProfile.DoesNotExist:
        message.reply_channel.send({
            "text": json.dumps({"error": "bad_slug"}),
            "close": True,
        })
        return
    # accept connection
    message.reply_channel.send({"accept": True})
    Group(profile.notification_channel).add(message.reply_channel)