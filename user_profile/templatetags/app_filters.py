from datetime import date, timedelta

from django import template
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from user_profile.models import UserProfile

register = template.Library()


@register.filter(name='file_exists')
def file_exists(value):
    return default_storage.exists(value)


@register.filter(name='url_exists')
def url_exists(value):
    # NO LO HE PROBADO TODAVIA, PUEDE QUE NO FUNCIONE
    validate = URLValidator(verify_exists=True)
    try:
        validate('http://www.somelink.com/to/my.pdf')
        return True
    except ValidationError:
        return False

# Comprobar si sigo al autor de la publicacion
@register.filter(name='check_follow')
def check_follow(request, author):

    print('Request username: ' + request + ' author username: ' + author)
    # obtenemos el model del autor del comentario
    user_profile = get_object_or_404(
        get_user_model(), username__iexact=author)

    # Si el perfil es privado, directamente no se puede ver...
    if user_profile.profile.privacity == 'N':
        return False
    # Si el perfil es público, directamente se puede ver...
    elif user_profile.profile.privacity == 'A':
        return True

    request = get_object_or_404(
        get_user_model(), username__iexact=request)

    # saber si sigo al perfil que visito
    if request.username != user_profile.username:
        isFriend = False
        try:
            if request.profile.is_follow(user_profile.profile):
                isFriend = True
        except ObjectDoesNotExist:
            isFriend = False
    else:
        isFriend = False

     # saber si sigo al perfil que visito
    if request.username != user_profile.username:
        isFollower = False
        try:
            if request.profile.is_follow(user_profile.profile):
                isFollower = True
        except ObjectDoesNotExist:
                isFollower = False
    else:
            isFollower = False

    # Si sigo al autor de la publicacion y tiene la privacidad "OF"...
    if isFriend and user_profile.profile.privacity == 'OF':
        return True
    # Si sigo al autor de la publicacion o él me sigue a mi, y tiene la privacidad OFAF...
    elif (isFriend and user_profile.profile.privacity == 'OFAF') or (isFollower and user_profile.profile.privacity == 'OFAF'):
        return True
    # Si no cumple ningun caso...
    else:
        return False

@register.filter(name='check_blocked')
def check_blocked(request, author):
    user_profile = get_object_or_404(
        get_user_model(), username__iexact=author)
    request = get_object_or_404(
        get_user_model(), username__iexact=request)

    try:
        blocked = request.profile.is_blocked(user_profile.profile)
    except ObjectDoesNotExist:
        return False

    if blocked:
        return True
    else:
        return False

    return False

@register.filter(name='is_follow')
def is_follow(request, profile):
    user_profile = get_object_or_404(
        UserProfile, id=profile)
    
    if request.pk != user_profile.user.pk:
        isFriend = False
        try:
            if request.profile.is_follow(user_profile):
                return True
        except ObjectDoesNotExist:
            pass
    return False

@register.filter(name='exist_request')
def exist_request(request, profile):
    user_profile = get_object_or_404(
        UserProfile, id=profile)
    
    if request.pk != user_profile.user.pk:
        isFriend = False
        try:
            if request.profile.get_follow_request(user_profile):
                return True
        except ObjectDoesNotExist:
            pass
    return False

@register.filter(name='is_blocked')
def is_blocked(request, profile):
    user_profile = get_object_or_404(
        UserProfile, id=profile)

    try:
        if request.profile.is_blocked(user_profile):
            return True
    except ObjectDoesNotExist:
        pass

    return False