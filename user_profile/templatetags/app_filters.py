from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from neomodel import db
from user_profile.models import TagProfile
from depot.manager import DepotManager
from user_profile.models import NodeProfile, Request

register = template.Library()

CHOICES = (
        ('D', '<i class="fa fa-futbol-o" aria-hidden="true"></i>'),
        ('M', '<i class="fa fa-globe" aria-hidden="true"></i>'),
        ('MU', '<i class="fa fa-music" aria-hidden="true"></i>'),
        ('C', '<i class="fa fa-flask" aria-hidden="true"></i>'),
        ('L', '<i class="fa fa-pencil" aria-hidden="true"></i>'),
        ('T', '<i class="fa fa-laptop" aria-hidden="true"></i>'),
        ('CO', '<i class="fa fa-cutlery" aria-hidden="true"></i>'),
        ('MO', '<i class="fa fa-motorcycle" aria-hidden="true"></i>'),
        ('CON', '<i class="fa fa-users" aria-hidden="true"></i>'),
        ('F', '<i class="fa fa-glass" aria-hidden="true"></i>'),
        ('DM', '<i class="fa fa-hashtag" aria-hidden="true"></i>'),
        ('VJ', '<i class="fa fa-gamepad" aria-hidden="true"></i>'),
        ('FT', '<i class="fa fa-camera" aria-hidden="true"></i>'),
        ('CI', '<i class="fa fa-video-camera" aria-hidden="true"></i>'),
        ('A', '<i class="fa fa-paint-brush" aria-hidden="true"></i>'),
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
