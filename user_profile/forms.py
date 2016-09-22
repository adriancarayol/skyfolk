# encoding:utf-8
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.forms import FileInput

from user_profile.models import UserProfile


class SearchForm(forms.Form):
    """
    Formulario de búsqueda (input)
    que se muestra en el navegador principal de la página web,
    disponible en todas las secciones de la web.
    Como mínimo se debe introducir un caracter para realizar una búsqueda.
    """
    searchText = forms.CharField(label="", help_text="", required=False,
                                 widget=forms.TextInput(attrs={'placeholder': '¿Que es lo que quieres buscar?',
                                                               'pattern': '.{1,}',
                                                               'required title': '1 character minimum'}))


class SignupForm(forms.Form):
    """
    Formulario de registro.
    Se usa un validador (alphanumeric) para el nombre y apellido,
    el cual sólo permite introducir letras minúsculas/maýusculas, separadas
    por espacios.
    """
    alphanumeric = RegexValidator(r'^(\s*[^\W\d_]+(([\'\-\+\s]\s*[^\W\d_])?[^\W\d_]*)\s*)+$',
                                  message='Tu nombre/apellido sólo puede contener letras.')
    first_name = forms.CharField(label=_('Nombre'), min_length=1, max_length=35, help_text="",
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': _('Nombre')}), validators=[alphanumeric])
    last_name = forms.CharField(label=_('Apellido'), min_length=1, max_length=35, help_text="",
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': _('Apellido')}), validators=[alphanumeric])

    def save(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class UserForm(forms.ModelForm):
    """
    Formulario usado en la configuración del usuario,
    permite cambiar el nombre/apellido del usuario.
    """
    alphanumeric = RegexValidator(r'^(\s*[^\W\d_]+(([\'\-\+\s]\s*[^\W\d_])?[^\W\d_]*)\s*)+$',
                                  message='Tu nombre/apellido sólo puede contener letras.')
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual', 'maxlength': '30'}),
                                 validators=[alphanumeric])
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'actual', 'maxlength': '30'}),
                                validators=[alphanumeric])

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ProfileForm(forms.ModelForm):
    """
    Formulario, que junto con <<UserForm>>, sirven para
    cambiar datos del usuario en configuración.
    <<status>>, sirve para cambiar el estado del usuario
    <<hiddenMenu>>, sirve para escoger que tipo de menú desea visualizar
    en la web.
    """
    status = forms.CharField(widget=forms.TextInput(attrs={'class': 'status',
                                                           'placeholder': 'Estado',
                                                           'maxlength': '20'}), required=False)

    class Meta:
        model = UserProfile
        fields = ('backImage', 'status', )  # Añadir 'image' si decidimos quitar django-avatar.
        # fields = ('image', 'backImage', 'status')


class PrivacityForm(forms.ModelForm):
    """
    Formulario para escoger la privacidad deseada del usuario.
    Se encuentra en configuración, y las opciones son las que
    se describen abajo.
    """
    CHOICES = (
        ('A', 'Todos pueden ver mi perfil y mis publicaciones.'),
        ('OF', 'Sólo mis seguidores pueden ver mi perfil y mis publicaciones.'),
        ('OFAF', 'Sólo mis seguidores y aquellas personas que sigo pueden ver mi perfil y mis publicaciones.'),
        ('N', 'Nadie puede ver ni mi perfil ni mis publicaciones.'),
    )

    privacity = forms.ChoiceField(choices=CHOICES, required=True, label='Escoge una opción de privacidad.')

    class Meta:
        model = UserProfile
        fields = ('privacity', )


class DeactivateUserForm(forms.ModelForm):
    """
    Formulario para desactivar la cuenta del usuario.
    """
    class Meta:
        model = User
        fields = ['is_active']

    def __init__(self, *args, **kwargs):
        super(DeactivateUserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].help_text = \
            '<b>Desmarque esta opción si quiere eliminar permanentemente su cuenta.</b>'

    def clean_is_active(self):
        is_active = not (self.cleaned_data["is_active"])
        return is_active
