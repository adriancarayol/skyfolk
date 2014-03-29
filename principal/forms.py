#encoding:utf-8
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


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


class SearchForm(forms.Form):

    searchText = forms.CharField(label="", help_text="",required=False,widget=forms.TextInput(attrs={'placeholder' : '¿Que es lo que quieres buscar?'}))


attrs_dict = {'class': 'required'}
##########################################################################
# Formulario de autenticacion que sobreescribe al de userena
#   Carlos Canicio                                       
##########################################################################
class AuthenticationForm(forms.Form):

    #identification = my_identification_field_factory(_(u"Email or username"),
    #                                              _(u"Either supply us with your email or username."))


    identification = forms.CharField(label="",
                           widget=forms.TextInput(attrs={'placeholder' : _(u"Email or username")}),
                           max_length=75,
                           help_text="",
                           error_messages={'required': _("%(error)s") % {'error': _(u"Either supply us with your email or username.")}})

    password = forms.CharField(label="",
                               help_text="", widget=forms.PasswordInput(attrs={'placeholder' : 'Password'}, render_value=False))
    
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(),
                                     required=False,
                                     label=_(u'Remember me for %(days)s') % {'days': _(settings.USERENA_REMEMBER_ME_DAYS[0])})

    def __init__(self, *args, **kwargs):
        """ A custom init because we need to change the label if no usernames is used """
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        # Dirty hack, somehow the label doesn't get translated without declaring
        # it again here.
        self.fields['remember_me'].label = _(u'Remember me for %(days)s') % {'days': _(settings.USERENA_REMEMBER_ME_DAYS[0])}
        if settings.USERENA_WITHOUT_USERNAMES:
            #self.fields['identification'] = identification_field_factory(_(u"Email"), _(u"Please supply your email."))
            self.fields['identification'] = forms.CharField(label="",
                           widget=forms.TextInput(attrs={'placeholder' : _(u"Email")}),
                           max_length=75,
                           help_text="",
                           error_messages={'required': _("%(error)s") % {'error': _(u"Please supply your email.")}})



    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(identification=identification, password=password)
            if user is None:
                raise forms.ValidationError(_(u"Please enter a correct username or email and password. Note that both fields are case-sensitive."))
        return self.cleaned_data


