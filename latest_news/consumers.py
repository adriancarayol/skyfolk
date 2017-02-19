import json

from channels import Group
from channels.auth import channel_session_user_from_http
from django.core.exceptions import ObjectDoesNotExist

from user_profile.models import UserProfile


@channel_session_user_from_http
def ws_connect_news(message):
    """
    Establece una conexion para recibibir
    actualizaciones en el tablon inicio
    """
    username = message.user.username
    try:
        profile = UserProfile.objects.get(user__username__iexact=username)
    except ObjectDoesNotExist:
        message.reply_channel.send({
            "text": json.dumps({"error": "bad_slug"}),
            "close": True,
        })
        return
    message.reply_channel.send({"accept": True})
    Group(profile.news_channel).add(message.reply_channel)
