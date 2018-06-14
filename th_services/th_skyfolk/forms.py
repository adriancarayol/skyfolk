# coding: utf-8

from django import forms
from django.forms import TextInput
from th_services.th_skyfolk.models import Skyfolk


class SkyfolkForm(forms.ModelForm):

    """
        for to handle {{ class_name }} service
    """

    class Meta:
        model = Skyfolk
        fields = ('name',)
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
        }


class SkyfolkProviderForm(SkyfolkForm):
    pass


class SkyfolkConsumerForm(SkyfolkForm):
    pass
