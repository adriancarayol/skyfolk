#encoding:utf-8
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm


class UserCreateForm(UserCreationForm):
	
    email = forms.EmailField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder' : 'Email'}))
    username = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder' : 'Nick'}))
    password1 = forms.CharField(label="", help_text="",required=True,widget=forms.PasswordInput(attrs={'placeholder' : 'Contraseña'}))
    password2 = forms.CharField(label="", help_text="",required=True,widget=forms.PasswordInput(attrs={'placeholder' : 'Repita contraseña'}))
    first_name = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder' : 'Nombre'}))
    last_name = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder' : 'Apellidos'}))
    

    #email = forms.EmailField(label = "Email")
    #fullname = forms.CharField(label = "First name")

     # this sets the order of the fields
    class Meta:
        model = User
        fields = ( "first_name", "last_name", "username", "password1", "password2", "email" )
        #fields = ( "username", "email" )

    # this redefines the save function to include the fields you added
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.first_name = self.cleaned_data["first_name"].lower()
        user.last_name = self.cleaned_data["last_name"].lower()
        user.username = self.cleaned_data["username"].lower()
        user.password1 = self.cleaned_data["password1"]
        user.password2 = self.cleaned_data["password2"]        
 
        if commit:
            user.save()
        return user

class AuthForm(AuthenticationForm):

    #username = forms.CharField(widget=TextInput(attrs={'class': 'span2','placeholder': 'Email'}))
    #password = forms.CharField(widget=PasswordInput(attrs={'class': 'span2','placeholder':'Password'}))

    username = forms.CharField(label="", help_text="",widget=forms.TextInput(attrs={'placeholder' : 'Nick'}))
    password = forms.CharField(label="", help_text="",widget=forms.PasswordInput(attrs={'placeholder' : 'Contraseña'}))


"""
class AuthForm(AuthenticationForm):

    #username = forms.CharField(widget=TextInput(attrs={'class': 'span2','placeholder': 'Email'}))
    #password = forms.CharField(widget=PasswordInput(attrs={'class': 'span2','placeholder':'Password'}))
    def __init__(self, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)
        
        #username = forms.CharField(label="", help_text="",widget=forms.TextInput(attrs={'placeholder' : 'Nick'}))
        #password = forms.CharField(label="", help_text="",widget=forms.PasswordInput(attrs={'placeholder' : 'Contraseña'}))

        self.base_fields['username'].widget.attrs['placeholder'] = 'Nick'
        self.base_fields['password'].widget.attrs['placeholder'] = 'Contraseña'
        self.base_fields['username'].label = ''
        self.base_fields['password'].label = ''
"""