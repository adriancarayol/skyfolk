# coding: utf-8

from django import forms
from django.forms import TextInput
from th_services.th_wallabag.models import Wallabag
from django.utils.translation import ugettext as _


class WallabagForm(forms.ModelForm):
    """
        for to handle Wallabag service
    """

    class Meta:
        model = Wallabag
        fields = ('tag',)
        labels = {
            'tag': _('Tag')
        }
        widgets = {
            'tag': TextInput(attrs={'class': 'form-control'}),
        }


class WallabagProviderForm(WallabagForm):
    pass


class WallabagConsumerForm(WallabagForm):
    pass
