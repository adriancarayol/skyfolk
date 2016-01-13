#encoding:utf-8
from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext

from user_profile.models import UserProfile


class SearchForm(forms.Form):

    searchText = forms.CharField(label="", help_text="",required=False,widget=forms.TextInput(attrs={'placeholder' : '¿Que es lo que quieres buscar?'}))


class SignupForm(forms.Form):
    #first_name = forms.CharField(max_length=30, label='Voornaam')
    #last_name = forms.CharField(max_length=30, label='Achternaam')
    first_name = forms.CharField(label=_('Firstname'), help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Firstname')}))
    last_name = forms.CharField(label=_('Lastname'), help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Lastname')}))
    def save(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.profile.image = None
        user.save()


class UserForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    status = forms.CharField(widget=forms.TextInput(attrs={'class': 'status', 'placeholder' : 'Estado', 'maxlength' : '20'}), required=False)
    hiddenMenu = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'hiddeMenu'}), required=False)
    
    class Meta:
        model = UserProfile
        fields = ('image', 'backImage', 'status', 'hiddenMenu')
