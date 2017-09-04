import json
from distutils.version import StrictVersion

from channels import Group as group_channel
from django import get_version
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timesince import timesince as timesince_
from avatar.models import Avatar
from avatar.templatetags.avatar_tags import avatar
from user_profile.utils import notification_channel

if StrictVersion(get_version()) >= StrictVersion('1.8.0'):
    from django.contrib.contenttypes.fields import GenericForeignKey
else:
    from django.contrib.contenttypes.generic import GenericForeignKey

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.six import text_type
from .utils import id2slug

from .signals import notify

from model_utils import Choices
from jsonfield.fields import JSONField

from django.contrib.auth.models import Group


# SOFT_DELETE = getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False)
def is_soft_delete():
    # TODO: SOFT_DELETE = getattr(settings, ...) doesn't work with "override_settings" decorator in unittest
    #     But is_soft_delete is neither a very elegant way. Should try to find better approach
    return getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False)


def assert_soft_delete():
    if not is_soft_delete():
        msg = """To use 'deleted' field, please set 'NOTIFICATIONS_SOFT_DELETE'=True in settings.
        Otherwise NotificationQuerySet.unread and NotificationQuerySet.read do NOT filter by 'deleted' field.
        """
        raise ImproperlyConfigured(msg)


class NotificationQuerySet(models.query.QuerySet):

    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """Return only unread items in the current queryset"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=True, deleted=False).prefetch_related('actor')
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=True).prefetch_related('actor')

    def unread_limit(self, include_deleted=False, limit=20):
        """
        Devuelve n limitaciones delimitadas por el parametro
        limit, por defecto devolvera 20 notificaciones
        :return Devuelve solo las notificaciones no leidas:
        """
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=True, deleted=False).prefetch_related('actor')[:limit]
        else:
            return self.filter(unread=True).prefetch_related('actor')[:limit]

    def read(self, include_deleted=False):
        """Return only read items in the current queryset"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=False, deleted=False).prefetch_related('actor')
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=False).prefetch_related('actor')

    def mark_all_as_read(self, recipient=None):
        """Mark as read any unread messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qs = self.unread(True)
        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        """Mark as unread any read messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        qs = self.read(True)

        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(unread=True)

    def deleted(self):
        """Return only deleted items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=True).prefetch_related('actor')

    def active(self):
        """Return only active(un-deleted) items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=False).prefetch_related('actor')

    def mark_all_as_deleted(self, recipient=None):
        """Mark current queryset as deleted.
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qs = self.active()
        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(deleted=True)

    def mark_all_as_active(self, recipient=None):
        """Mark current queryset as active(un-deleted).
        Optionally, filter by recipient first.
        """
        assert_soft_delete()
        qs = self.deleted()
        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(deleted=False)

    def mark_as_unsent(self):
        return self.update(emailed=False)

    def mark_as_sent(self):
        return self.update(emailed=True)


class Notification(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional
    target).
    Nomenclature based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format::

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::

        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 2 hours ago>

    Unicode Representation::

        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    HTML Representation::

        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """
    LEVELS = Choices('success', 'info', 'warning', 'error')
    level = models.CharField(choices=LEVELS, default=LEVELS.info, max_length=20)

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, related_name='notifications')
    unread = models.BooleanField(default=True, blank=False)

    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor')
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')
    actor_avatar = models.CharField(max_length=255, blank=True, null=True)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(ContentType, related_name='notify_target', blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                                   related_name='notify_action_object')
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    timestamp = models.DateTimeField(default=timezone.now)

    public = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)

    data = JSONField(blank=True, null=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ('-timestamp', )
        app_label = 'notifications'

    def __unicode__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince(),
            'actor_avatar': self.actor_avatar
        }
        if self.target:
            if self.action_object:
                return u'%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago' % ctx
            return u'%(actor)s %(verb)s %(target)s %(timesince)s ago' % ctx
        if self.action_object:
            return u'%(actor)s %(verb)s %(action_object)s %(timesince)s ago' % ctx
        return u'%(actor)s %(verb)s %(timesince)s ago' % ctx

    def __str__(self):  # Adds support for Python 3
        return self.__unicode__()

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return timesince_(self.timestamp, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()

# 'NOTIFY_USE_JSONFIELD' is for backward compatibility
# As app name is 'notifications', let's use 'NOTIFICATIONS' consistently from now
EXTRA_DATA = getattr(settings, 'NOTIFY_USE_JSONFIELD', None)
if EXTRA_DATA is None:
    EXTRA_DATA = getattr(settings, 'NOTIFICATIONS_USE_JSONFIELD', False)


def notify_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    # Pull the options out of kwargs
    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    optional_objs = [
        (kwargs.pop(opt, None), opt)
        for opt in ('target', 'action_object')
        ]
    public = bool(kwargs.pop('public', True))
    description = kwargs.pop('description', None)
    timestamp = kwargs.pop('timestamp', timezone.now())
    level = kwargs.pop('level', Notification.LEVELS.info)
    send_channel = kwargs.pop('send_to_channel', True)
    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    else:
        recipients = [recipient]

    for recipient in recipients:
        actor_avatar = avatar(actor)
        newnotify, created = Notification.objects.get_or_create(
            recipient=recipient,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            actor_avatar=actor_avatar,  # URL del avatar del usuario que hace la peticion
            verb=text_type(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(newnotify, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj))

        if len(kwargs) and EXTRA_DATA:
            newnotify.data = kwargs

        newnotify.save()

        content = render_to_string(template_name='channels/new_notification.html',
            context={'notification': newnotify})

        data = {
            'content': content,
            'id': newnotify.id
        }
        # Enviamos notificacion al canal del receptor
        if send_channel:
            group_channel(notification_channel(recipient.id)).send({
                "text": json.dumps(data)
            })
        return newnotify  # add by adrian


# connect the signal
notify.connect(notify_handler, dispatch_uid='notifications.models.notification')
