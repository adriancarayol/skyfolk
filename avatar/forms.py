import os
from os.path import splitext
from urllib.parse import urlparse

import requests
from django import forms
from django.forms import widgets
from django.template.defaultfilters import filesizeformat
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from avatar.conf import settings
from avatar.models import Avatar
from photologue.utils.utils import split_url
from photologue.validators import valid_url_extension, valid_url_mimetype


def avatar_img(avatar, size):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return mark_safe('<img src="%s" alt="%s" width="%s" height="%s" />' %
                     (avatar.avatar_url(size), six.text_type(avatar),
                      size, size))


class UploadAvatarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UploadAvatarForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UploadAvatarForm, self).clean()
        image = cleaned_data.get('avatar', None)
        url_image = cleaned_data.get('url_image', None)

        if not image and not url_image:
            raise forms.ValidationError('Debes seleccionar una imagen o introducir una URL.')

        return cleaned_data

    def clean_avatar(self):
        data = self.cleaned_data['avatar']

        if not data:
            return

        if settings.AVATAR_ALLOWED_FILE_EXTS:
            root, ext = os.path.splitext(data.name.lower())
            if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                valid_exts = ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)
                error = _("%(ext)s is an invalid file extension. "
                          "Authorized extensions are : %(valid_exts_list)s")
                raise forms.ValidationError(error %
                                            {'ext': ext,
                                             'valid_exts_list': valid_exts})

        if data.size > settings.AVATAR_MAX_SIZE:
            error = _("Your file is too big (%(size)s), "
                      "the maximum allowed size is %(max_valid_size)s")
            raise forms.ValidationError(error % {
                'size': filesizeformat(data.size),
                'max_valid_size': filesizeformat(settings.AVATAR_MAX_SIZE)
            })

        count = Avatar.objects.filter(user=self.user).count()
        if (1 < settings.AVATAR_MAX_AVATARS_PER_USER <= count):
            error = _("You already have %(nb_avatars)d avatars, "
                      "and the maximum allowed is %(nb_max_avatars)d.")
            raise forms.ValidationError(error % {
                'nb_avatars': count,
                'nb_max_avatars': settings.AVATAR_MAX_AVATARS_PER_USER,
            })
        return data

    def clean_url_image(self):
        url_image = self.cleaned_data['url_image']

        if not url_image:
            return

        domain, path = split_url(url_image)
        if not valid_url_extension(url_image) or not valid_url_mimetype(url_image):
            raise forms.ValidationError(
                _("Not a valid Image. The URL must have an image extensions (.jpg/.jpeg/.png)"))

        count = Avatar.objects.filter(user=self.user).count()
        if 1 < settings.AVATAR_MAX_AVATARS_PER_USER <= count:
            error = _("You already have %(nb_avatars)d avatars, "
                      "and the maximum allowed is %(nb_max_avatars)d.")
            raise forms.ValidationError(error % {
                'nb_avatars': count,
                'nb_max_avatars': settings.AVATAR_MAX_AVATARS_PER_USER,
            })

        return url_image

    class Meta:
        model = Avatar
        fields = ('url_image', 'avatar')


class PrimaryAvatarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.pop('user')
        size = kwargs.pop('size', settings.AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop('avatars')
        super(PrimaryAvatarForm, self).__init__(*args, **kwargs)
        choices = [(avatar.id, avatar_img(avatar, size)) for avatar in avatars]
        self.fields['choice'] = forms.ChoiceField(label=_("Choices"),
                                                  choices=choices,
                                                  widget=widgets.RadioSelect)


class DeleteAvatarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.pop('user')
        size = kwargs.pop('size', settings.AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop('avatars')
        super(DeleteAvatarForm, self).__init__(*args, **kwargs)
        choices = [(avatar.id, avatar_img(avatar, size)) for avatar in avatars]
        self.fields['choices'] = forms.MultipleChoiceField(label=_("Choices"),
                                                           choices=choices,
                                                           widget=widgets.CheckboxSelectMultiple)
