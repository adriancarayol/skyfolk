# coding: utf-8

from django import forms
from django.forms import TextInput
from th_services.th_tumblr.models import Tumblr
from django.utils.translation import ugettext_lazy as _


class TumblrForm(forms.ModelForm):

    """
        for to handle Tumblr service
    """

    class Meta:
        model = Tumblr
        fields = ('blogname', 'tag')
        labels = {
            'blogname': _('Blogname'),
            'tag': _('Etiqueta')
        }
        widgets = {
            'blogname': TextInput(attrs={'class': 'form-control'}),
            'tag': TextInput(attrs={'class': 'form-control'}),
        }


class TumblrProviderForm(TumblrForm):
    pass


class TumblrConsumerForm(TumblrForm):
    pass
