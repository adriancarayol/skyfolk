# coding: utf-8

from django import forms
from django.forms import TextInput
from th_services.th_evernote.models import Evernote
from django.utils.translation import ugettext_lazy as _


class EvernoteForm(forms.ModelForm):
    """
        for to handle Evernote service
    """

    class Meta:
        model = Evernote
        fields = ('tag', 'notebook',)
        labels = {
            'tag': _('Tag'),
            'notebook': _('Notebook')
        }
        widgets = {
            'tag': TextInput(attrs={'class': 'form-control'}),
            'notebook': TextInput(attrs={'class': 'form-control'}),
        }


class EvernoteConsumerForm(EvernoteForm):
    pass


class EvernoteProviderForm(EvernoteForm):
    pass
