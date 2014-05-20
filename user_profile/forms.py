#encoding:utf-8
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext
from allauth.account.forms import LoginForm
from django import forms
from allauth.account.signals import password_changed
from django.dispatch import receiver
from django.contrib import messages
from django.db import models
from django.forms import ModelForm
from user_profile.models import UserProfile
from django.contrib.auth.models import User

class SearchForm(forms.Form):

    searchText = forms.CharField(label="", help_text="",required=False,widget=forms.TextInput(attrs={'placeholder' : '¿Que es lo que quieres buscar?'}))


"""
class MyLoginForm(LoginForm):

    # Override attributes
    #existing_field = forms.CharField(widget=widgets.CustomWidget())
    #username = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder' : 'Nick'}))


    #password = PasswordField()
    #login_widget = forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'})
    #login = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'}))
    #login_field = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'}))
    #login_widget = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'}))
    #login_field = forms.CharField(label="", help_text="",widget=login_widget,max_length=30)

    # Add Custom Attributes
    #new_field = forms.CharField(widget=widgets.CustomWidget())

"""


class SignupForm(forms.Form):
    #first_name = forms.CharField(max_length=30, label='Voornaam')
    #last_name = forms.CharField(max_length=30, label='Achternaam')
    first_name = forms.CharField(label=_('Firstname'), help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Firstname')}))
    last_name = forms.CharField(label=_('Lastname'), help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Lastname')}))


    def save(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual'}))
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        #fields = ('user','image')
        exclude = ('user',)
