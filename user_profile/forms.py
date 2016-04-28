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
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual', 'maxlength': '30'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual', 'maxlength': '30'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    status = forms.CharField(widget=forms.TextInput(attrs={'class': 'status', 'placeholder' : 'Estado', 'maxlength' : '20'}), required=False)
    hiddenMenu = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'hiddeMenu'}), required=False)

    class Meta:
        model = UserProfile
        fields = ('backImage', 'status', 'hiddenMenu') # Añadir 'image' si decidimos quitar django-avatar.
        #fields = ('image', 'backImage', 'status')


class PrivacityForm(forms.ModelForm):
   
    CHOICES = (
            ('A', 'Todos pueden ver mi perfil y mis publicaciones.'),
            ('OF', 'Sólo mis seguidores pueden ver mi perfil y mis publicaciones.'),
            ('OFAF', 'Sólo mis seguidores y aquellas personas que sigo pueden ver mi perfil y mis publicaciones.'),
            ('N', 'Nadie puede ver ni mi perfil ni mis publicaciones.'),
            )
    privacity = forms.ChoiceField(choices=CHOICES, required=True, label='Escoge una opción de privacidad.')
    class Meta:
        model = UserProfile
        fields = ('privacity',)
