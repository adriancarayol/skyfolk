import os
import requests

from django import forms
from django.forms import widgets
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from avatar.conf import settings
from avatar.models import Avatar
from urllib.parse import urlparse
from os.path import splitext

def avatar_img(avatar, size):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return mark_safe('<img src="%s" alt="%s" width="%s" height="%s" />' %
                     (avatar.avatar_url(size), six.text_type(avatar),
                      size, size))


class UploadAvatarForm(forms.Form):

    avatar = forms.ImageField(label=_("avatar"), required=False, widget=forms.FileInput(attrs={'class': 'file_avatar'}))
    url_image = forms.URLField(label=_("URL imagen"), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UploadAvatarForm, self).__init__(*args, **kwargs)

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
        if (settings.AVATAR_MAX_AVATARS_PER_USER > 1 and
                count >= settings.AVATAR_MAX_AVATARS_PER_USER):
            error = _("You already have %(nb_avatars)d avatars, "
                      "and the maximum allowed is %(nb_max_avatars)d.")
            raise forms.ValidationError(error % {
                'nb_avatars': count,
                'nb_max_avatars': settings.AVATAR_MAX_AVATARS_PER_USER,
            })
        return

    def clean_url_image(self):
        url_image = self.cleaned_data['url_image']

        if not url_image:
            return

        parsed = urlparse(url_image)
        name, ext = splitext(parsed.path)

        if not ext:
            valid_exts = None
            if settings.AVATAR_ALLOWED_FILE_EXTS:
                valid_exts = ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)
            error = _("%(ext)s is an invalid file extension. "
                      "Authorized extensions are : %(valid_exts_list)s")
            raise forms.ValidationError(error %
                                        {'ext': ext,
                                         'valid_exts_list': valid_exts})

        if settings.AVATAR_ALLOWED_FILE_EXTS:
            if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                valid_exts = ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)
                error = _("%(ext)s is an invalid file extension. "
                      "Authorized extensions are : %(valid_exts_list)s")
                raise forms.ValidationError(error %
                                        {'ext': ext,
                                         'valid_exts_list': valid_exts})

        response = requests.head(url_image)

        if int(response.headers.get('content-length', None)) > settings.AVATAR_MAX_SIZE:
            error = _("Your file is too big (%(size)s), "
                      "the maximum allowed size is %(max_valid_size)s")
            raise forms.ValidationError(error % {
                'size': filesizeformat(response.headers.get('content-length', None)),
                'max_valid_size': filesizeformat(settings.AVATAR_MAX_SIZE)
            })

        count = Avatar.objects.filter(user=self.user).count()
        if 1 < settings.AVATAR_MAX_AVATARS_PER_USER <= count:
            error = _("You already have %(nb_avatars)d avatars, "
                      "and the maximum allowed is %(nb_max_avatars)d.")
            raise forms.ValidationError(error % {
                'nb_avatars': count,
                'nb_max_avatars': settings.AVATAR_MAX_AVATARS_PER_USER,
            })

        return


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
