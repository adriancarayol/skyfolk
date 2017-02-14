from django import template

register = template.Library()


@register.simple_tag(takes_context=True, name='unread_notifications')
def unread_notifications(context):
    """
    Devolvemos las notificaciones no leidas del usuario
    :param context:
    :return: Notificaciones no leidas del usuario
    """
    request = context['request']
    return request.user.notifications.unread().count()
