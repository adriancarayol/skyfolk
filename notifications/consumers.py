import json

from channels import Group
from channels.auth import channel_session_user_from_http

from user_profile.models import NodeProfile


# The "slug" keyword argument here comes from the regex capture group in
#
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
