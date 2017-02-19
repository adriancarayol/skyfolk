from avatar.models import Avatar
from user_profile.models import UserProfile


def get_author_avatar(authorpk):
    """
    Devuelve el avatar del autor de la publicacion pasada como parametro
    """
    try:
        avatars = Avatar.objects.get(user=authorpk, primary=True)
    except Avatar.DoesNotExist:
        avatars = None

    if avatars:
        return avatars.get_absolute_url()
    else:
        return UserProfile.objects.get(user=authorpk).gravatar
