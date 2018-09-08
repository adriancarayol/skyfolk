# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import TextInput
from th_services.th_pushbullet.models import Pushbullet

PUSH_TYPE = (('note', _('Note')), ('link', _('Link')), ('file', _('File')))


class PushbulletForm(forms.ModelForm):

    """
        for to handle Todoist service
    """
    type = forms.ChoiceField(widget=forms.Select(
        attrs={'class': 'form-control'}))

    class Meta:
        model = Pushbullet
        fields = ('type', 'device', 'email', 'channel_tag')
        labels = {
            'type': _('Type'),
            'device': _('Device'),
            'email': _('Email'),
            'channel_tag': _('Channel')
        }
        widgets = {
            'device': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'channel_tag': TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PushbulletForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = PUSH_TYPE


class PushbulletProviderForm(PushbulletForm):
    pass


class PushbulletConsumerForm(PushbulletForm):
    pass
