from django.utils.translation import pgettext, ugettext_lazy as _, ugettext
from allauth.account.forms import LoginForm
from django import forms



class MyLoginForm(LoginForm):

    # Override attributes
    #existing_field = forms.CharField(widget=widgets.CustomWidget())
    #username = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder' : 'Nick'}))


    #password = PasswordField()
    #login_widget = forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'})
    login = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'}))
    login_field = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'}))
    login_widget = forms.CharField(label="", help_text="",required=True,widget=forms.TextInput(attrs={'placeholder':_('Username'),'autofocus': 'autofocus'}))
    #login_field = forms.CharField(label="", help_text="",widget=login_widget,max_length=30)

    # Add Custom Attributes
    #new_field = forms.CharField(widget=widgets.CustomWidget())





