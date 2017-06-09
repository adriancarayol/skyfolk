import json

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from user_profile.models import NodeProfile


@channel_session_user_from_http
def ws_connect_news(message):
    """
    Establece una conexion para recibibir
    actualizaciones en el tablon inicio
    """
    username = message.user.username
    try:
        profile = NodeProfile.nodes.get(title=username)
    except NodeProfile.DoesNotExist:
        message.reply_channel.send({
            "text": json.dumps({"error": "bad_slug"}),
            "close": True,
        })
        return
    message.reply_channel.send({"accept": True})
    Group(profile.news_channel).add(message.reply_channel)

@channel_session_user
def disconnect_news(message):
    """
    Removes the user from the liveblog group when they disconnect.

    Channels will auto-cleanup eventually, but it can take a while, and having old
    entries cluttering up your group will reduce performance.
    """
    username = message.user.username
    try:
        profile_blog =  NodeProfile.nodes.get(title=username)
    except NodeProfile.DoesNotExist:
        # This is the disconnect message, so the socket is already gone; we can't
        # send an error back. Instead, we just return from the consumer.
        return
    # It's called .discard() because if the reply channel is already there it
    # won't fail - just like the set() type.
    Group(profile_blog.news_channel).discard(message.reply_channel)