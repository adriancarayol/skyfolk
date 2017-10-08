import tempfile
from os.path import splitext
from urllib.parse import urlparse

import requests
from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import File
from django.shortcuts import render, redirect
from django.utils import six
from django.utils.translation import ugettext as _

from avatar.conf import settings
from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm, UploadAvatarForm
from avatar.models import Avatar
from avatar.signals import avatar_updated
from avatar.utils import (get_primary_avatar, get_default_avatar_url,
                          invalidate_cache)
from photologue.validators import validate_file_extension, validate_video, validate_extension, image_exists, \
    valid_image_mimetype, \
    valid_image_size
from photologue.utils.utils import split_url, get_url_tail, retrieve_image, pil_to_django


def _get_next(request):
    """
    The part that's the least straightforward about views in this module is
    how they determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the
    following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the
       view will redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters,
       the view will redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers,
       the view will redirect to that previous page.
    """
    next = request.POST.get('next', request.GET.get('next',
                                                    request.META.get('HTTP_REFERER', None)))
    if not next:
        next = request.path
    return next


def _get_avatars(user):
    # Default set. Needs to be sliced, but that's it. Keep the natural order.
    avatars = user.avatar_set.all()

    # Current avatar
    primary_avatar = avatars.order_by('-primary')[:1]
    if primary_avatar:
        avatar = primary_avatar[0]
    else:
        avatar = None

    if settings.AVATAR_MAX_AVATARS_PER_USER == 1:
        avatars = primary_avatar
    else:
        # Slice the default set now that we used
        # the queryset for the primary avatar
        avatars = avatars[:settings.AVATAR_MAX_AVATARS_PER_USER]
    return (avatar, avatars)


@login_required(login_url='/')
def add(request, extra_context=None, next_override=None,
        upload_form=UploadAvatarForm, *args, **kwargs):
    user = request.user

    if extra_context is None:
        extra_context = {}

    avatar, avatars = _get_avatars(user)

    if request.method == "POST":
        upload_avatar_form = upload_form(request.POST, request.FILES, user=request.user)
    else:
        upload_avatar_form = upload_form(user=request.user)

    # Si el formulario contiene un archivo
    if request.method == "POST" and 'avatar' in request.FILES:
        if upload_avatar_form.is_valid():
            avatar = upload_avatar_form.save(commit=False)
            avatar.user = user
            avatar.primary = True
            image_file = upload_avatar_form.cleaned_data['avatar']
            avatar.avatar.save(image_file.name, image_file)
            avatar.save()
            messages.success(request, _("Successfully uploaded a new avatar."))
            avatar_updated.send(sender=Avatar, user=user, avatar=avatar)
            return redirect(next_override or _get_next(request))

    if request.method == "POST" and 'avatar' not in request.FILES \
            and 'url_image' in request.POST:
        if upload_avatar_form.is_valid():
            url_image = upload_avatar_form.cleaned_data['url_image']

            avatar = upload_avatar_form.save(commit=False)
            avatar.user = user
            avatar.primary = True
            avatar.url_image = url_image

            domain, path = split_url(url_image)
            filename = get_url_tail(path)

            if not image_exists(url_image):
                raise ValidationError(_("Couldn't retreive image. (There was an error reaching the server)"))

            fobject = retrieve_image(url_image)

            if not valid_image_mimetype(fobject):
                raise ValidationError(_("Downloaded file was not a valid image"))

            pil_image = Image.open(fobject)
            pil_image.thumbnail((120, 120), Image.ANTIALIAS)

            if not valid_image_size(pil_image)[0]:
                raise ValidationError(_("Image is too large (> 5mb)"))

            django_file = pil_to_django(pil_image)

            avatar.avatar.save(filename, django_file)
            avatar.save()
            messages.success(request, _("Successfully uploaded a new avatar."))
            avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)

            return redirect(next_override or _get_next(request))

    context = {
        'avatar': avatar,
        'avatars': avatars,
        'upload_avatar_form': upload_avatar_form,
        'next': next_override or _get_next(request),
        'showPerfilButtons': True,
    }

    context.update(extra_context)
    return render(request, 'avatar/add.html', context)


@login_required(login_url='/')
def change(request, extra_context=None, next_override=None,
           upload_form=UploadAvatarForm, primary_form=PrimaryAvatarForm,
           *args, **kwargs):
    user = request.user
    if extra_context is None:
        extra_context = {}
    avatar, avatars = _get_avatars(user)
    if avatar:
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        kwargs = {}
    upload_avatar_form = upload_form(request.POST, request.FILES, user=request.user, **kwargs)
    primary_avatar_form = primary_form(request.POST or None,
                                       user=request.user,
                                       avatars=avatars, **kwargs)
    if request.method == "POST":
        updated = False
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(
                id=primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            updated = True
            invalidate_cache(request.user)
            messages.success(request, _("Successfully updated your avatar."))
        if updated:
            avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
        return redirect(next_override or _get_next(request))

    context = {
        'avatar': avatar,
        'avatars': avatars,
        'upload_avatar_form': upload_avatar_form,
        'primary_avatar_form': primary_avatar_form,
        'next': next_override or _get_next(request),
        'showPerfilButtons': True,
    }
    context.update(extra_context)
    return render(request, 'avatar/change.html', context)


@login_required(login_url='/')
def delete(request, extra_context=None, next_override=None, *args, **kwargs):
    user = request.user
    if extra_context is None:
        extra_context = {}
    avatar, avatars = _get_avatars(request.user)
    delete_avatar_form = DeleteAvatarForm(request.POST or None,
                                          user=request.user,
                                          avatars=avatars)
    if request.method == 'POST':
        if delete_avatar_form.is_valid():
            ids = delete_avatar_form.cleaned_data['choices']
            if six.text_type(avatar.id) in ids and avatars.count() > len(ids):
                # Find the next best avatar, and set it as the new primary
                for a in avatars:
                    if six.text_type(a.id) not in ids:
                        a.primary = True
                        a.save()
                        avatar_updated.send(sender=Avatar, user=request.user,
                                            avatar=avatar)
                        break
            Avatar.objects.filter(id__in=ids).delete()
            messages.success(request,
                             _("Successfully deleted the requested avatars."))
            return redirect(next_override or _get_next(request))

    context = {
        'avatar': avatar,
        'avatars': avatars,
        'delete_avatar_form': delete_avatar_form,
        'next': next_override or _get_next(request),
        'showPerfilButtons': True,
    }
    context.update(extra_context)

    return render(request, 'avatar/confirm_delete.html', context)


def render_primary(request, user=None, size=settings.AVATAR_DEFAULT_SIZE):
    size = int(size)
    avatar = get_primary_avatar(user, size=size)
    if avatar:
        # FIXME: later, add an option to render the resized avatar dynamically
        # instead of redirecting to an already created static file. This could
        # be useful in certain situations, particulary if there is a CDN and
        # we want to minimize the storage usage on our static server, letting
        # the CDN store those files instead
        url = avatar.avatar_url(size)
    else:
        url = get_default_avatar_url()

    return redirect(url)
