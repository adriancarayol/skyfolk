# coding: utf-8

from django import forms
from django.forms import TextInput
from th_services.th_pocket.models import Pocket
from django.utils.translation import ugettext_lazy as _


class PocketForm(forms.ModelForm):

    """
        for to handle Pocket service
    """

    class Meta:
        model = Pocket
        fields = ('tag',)
        labels = {
            'tag': _('Tag')
        }
        widgets = {
            'tag': TextInput(attrs={'class': 'form-control'}),
        }


class PocketProviderForm(PocketForm):
    pass


class PocketConsumerForm(PocketForm):
    pass
