# coding: utf-8

from django import forms
from django.forms import TextInput
from th_services.th_skyfolk.models import Skyfolk
from django.utils.translation import ugettext_lazy as _

class SkyfolkForm(forms.ModelForm):

    """
        for to handle {{ class_name }} service
    """

    class Meta:
        model = Skyfolk
        fields = ('name',)
        labels = {
            'name': _(u'Give your new pin a name'),
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
        }


class SkyfolkProviderForm(SkyfolkForm):
    pass


class SkyfolkConsumerForm(SkyfolkForm):
    pass
