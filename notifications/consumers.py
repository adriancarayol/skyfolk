import json
import logging
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from django.core.exceptions import ObjectDoesNotExist
from user_profile.models import UserProfile
# The "slug" keyword argument here comes from the regex capture group in
#
@channel_session_user_from_http
def ws_connect(message):
    username = message.user.username
    try:
        profile = UserProfile.objects.get(user__username__iexact=username)
    except ObjectDoesNotExist:
        message.reply_channel.send({
            "text": json.dumps({"error": "bad_slug"}),
            "close": True,
        })
        return
    # accept connection
    message.reply_channel.send({"accept": True})
    Group(profile.notification_channel).add(message.reply_channel)
