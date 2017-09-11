from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from neomodel import db

from user_profile.models import NodeProfile, Request
from user_profile.models import TagProfile

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


# Comprobar si sigo al autor de la publicacion
@register.filter(name='check_follow')
def check_follow(request, author):
    # obtenemos el model del autor del comentario
    try:
        user_profile = NodeProfile.nodes.get(user_id=author)
    except NodeProfile.DoesNotExist:
        return False

    # Si el perfil es privado, directamente no se puede ver...
    if user_profile.privacity == 'N':
        return False
    # Si el perfil es público, directamente se puede ver...
    elif user_profile.privacity == 'A':
        return True

    try:
        me = NodeProfile.nodes.get(user_id=request)
    except NodeProfile.DoesNotExist:
        return False

    # saber si sigo al perfil que visito
    if me.user_id != user_profile.user_id:
        try:
            isFriend = me.follow.is_connected(user_profile)
        except Exception:
            isFriend = False
    else:
        isFriend = False

    # Si sigo al autor de la publicacion y tiene la privacidad "OF"...
    if isFriend and user_profile.privacity == 'OF':
        return True

    # saber si el perfil me sigue
    if me.user_id != me.user_id:
        try:
            isFollower = user_profile.follow.is_connected(me)
        except ObjectDoesNotExist:
            isFollower = False
    else:
        isFollower = False

    # Si sigo al autor de la publicacion o él me sigue a mi, y tiene la privacidad OFAF...
    if (isFriend and user_profile.profile.privacity == 'OFAF') or (
                isFollower and user_profile.profile.privacity == 'OFAF'):
        return True
    # Si no cumple ningun caso...
    else:
        return False


@register.filter(name='check_blocked')
def check_blocked(request, author):
    try:
        user_profile = NodeProfile.nodes.get(user_id=author)
        me = NodeProfile.nodes.get(user_id=request)
    except NodeProfile.DoesNotExist:
        return False

    try:
        return me.bloq.is_connected(user_profile)
    except Exception:
        pass

    return False


@register.filter(name='is_follow')
def is_follow(request, profile):
    try:
        user_profile = NodeProfile.nodes.get(user_id=profile)
        me = NodeProfile.nodes.get(user_id=request)
    except NodeProfile.DoesNotExist:
        return False

    if me.user_id != user_profile.user_id:
        try:
            return me.follow.is_connected(user_profile)
        except Exception:
            pass
    return False


@register.filter(name='exist_request')
def exist_request(request, profile):
    try:
        m = NodeProfile.nodes.get(user_id=profile)
        n = NodeProfile.nodes.get(user_id=request)
    except NodeProfile.DoesNotExist:
        return False

    if n.user_id != m.user_id:
        try:
            return Request.objects.get_follow_request(from_profile=n.user_id, to_profile=m.user_id)
        except ObjectDoesNotExist:
            pass
    return False


@register.filter(name='is_blocked')
def is_blocked(request, profile):
    try:
        user_profile = NodeProfile.nodes.get(user_id=profile)
        me = NodeProfile.nodes.get(user_id=request)
    except NodeProfile.DoesNotExist:
        return False

    if me.user_id != user_profile.user_id:
        try:
            return me.bloq.is_connected(user_profile)
        except Exception:
            pass

    return False


@register.filter(name='get_tags')
def get_tags(request):
    """
    Muestra los intereses dado el uid del NodeProfile de un usuario.
    :param request uid del NodeProfile de un usuario:
    :return Lista de intereses del usuario:
    """
    r, m = db.cypher_query(
        "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile) WHERE u1.user_id=%s RETURN tag" % request
    )
    results = [TagProfile.inflate(row[0]) for row in r]
    return results


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
