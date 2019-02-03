from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import URLValidator

from user_profile.models import Request, Profile, RelationShipProfile

register = template.Library()

CHOICES = (
    ('D', '<i class="material-icons">fitness_center</i>'),
    ('M', '<i class="material-icons">language</i>'),
    ('MU', '<i class="material-icons">music_note</i>'),
    ('C', '<i class="material-icons">loupe</i>'),
    ('L', '<i class="material-icons">edit</i>'),
    ('T', '<i class="material-icons">laptop</i>'),
    ('CO', '<i class="material-icons">room_service</i>'),
    ('MO', '<i class="material-icons">motorcycle</i>'),
    ('CON', '<i class="material-icons">people</i>'),
    ('F', '<i class="material-icons">local_bar</i>'),
    ('DM', '<i class="material-icons">whatshot</i>'),
    ('VJ', '<i class="material-icons">videogame_asset</i>'),
    ('FT', '<i class="material-icons">camera_alt</i>'),
    ('CI', '<i class="material-icons">camera_roll</i>'),
    ('A', '<i class="material-icons">brush</i>'),
)


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


@register.filter(name='is_follow')
def is_follow(request, profile):
    try:
        user_profile = Profile.objects.get(id=profile)
        me = Profile.objects.get(id=request)
    except Profile.DoesNotExist:
        return False

    if me != user_profile:
        try:
            return RelationShipProfile.objects.is_follow(user_profile, me)
        except ObjectDoesNotExist:
            pass
    return False


@register.filter(name='exist_request')
def exist_request(request, profile):
    try:
        m = Profile.objects.get(user_id=profile)
        n = Profile.objects.get(user_id=request)
    except Profile.DoesNotExist:
        return False

    if n != m:
        try:
            return Request.objects.get_follow_request(from_profile=n.user, to_profile=m.user)
        except ObjectDoesNotExist:
            pass
    return False


@register.filter(name='is_blocked')
def is_blocked(request, profile):
    try:
        user_profile = Profile.objects.get(user_id=profile)
        me = Profile.objects.get(user_id=request)
    except ObjectDoesNotExist:
        return False

    if me != user_profile:
        try:
            return RelationShipProfile.objects.is_blocked(user_profile, me)
        except ObjectDoesNotExist:
            pass

    return False


@register.filter(name='get_tags')
def get_tags(request):
    """
    Muestra los intereses dado el user_id del NodeProfile de un usuario.
    :param request uid del NodeProfile de un usuario:
    :return Lista de intereses del usuario:
    """
    return Profile.objects.filter(user__id=request).values_list('tags__name', flat=True)


@register.filter
def classname(obj):
    return obj.__class__.__name__


@register.filter
def interest_to_icon(tag):
    return dict(CHOICES).get(tag)


@register.filter
def lookup(d, key):
    try:
        return d[key]
    except KeyError:
        return ''


@register.filter
def subtract(value, arg):
    return value - arg


@register.simple_tag
def reduce(a, b):
    return a - b
