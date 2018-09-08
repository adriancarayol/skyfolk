# coding: utf-8

from django import forms
from th_services.th_mastodon.models import Mastodon
from django.utils.translation import ugettext_lazy as _


class MastodonForm(forms.ModelForm):
    """
        form to handle Mastodon service
    """

    class Meta:
        model = Mastodon
        labels = {
            'timeline': _('Timeline'),
            'tooter': _('Tooter'),
            'tag': _('Tag'),
            'fav': _('Favorite')
        }
        fields = ['timeline', 'tooter', 'tag', 'fav']


class MastodonProviderForm(MastodonForm):
    pass


class MastodonConsumerForm(MastodonForm):
    pass
