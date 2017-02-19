# encoding:utf-8
from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _

from user_profile.models import UserProfile, AuthDevices


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        auth_browser = forms.CharField(required=False)
        self.fields["auth_browser"] = auth_browser
        self.fields["auth_browser"].widget = forms.HiddenInput()

    def login(self, request, redirect_url=None):
        user_profile = UserProfile.objects.get(user=self.user)
        auth_token_device = self.cleaned_data['auth_browser']
        if auth_token_device:
            try:
                components = auth_token_device.split()
                device, created = AuthDevices.objects.get_or_create(user_profile=user_profile,
                                                                    browser_token=components.pop(0))
                if created:
                    device.save()
                    send_mail(
                        '[Skyfolk] - Nuevo inicio de sesión.',
                        'Hemos detectado un nuevo inicio de sesión. \n' + ",".join(components).replace(",", " "),
                        'noreply@skyfolk.net',
                        [self.user.email],
                        fail_silently=False,
                    )
            except IntegrityError:
                pass
        else:
            # Aqui informamos al usuario por email de que
            # el fingerprint browser no se ha podido coger
            send_mail(
                '[Skyfolk] - Nuevo inicio de sesión',
                'Hemos detectado un nuevo inicio de sesión.',
                'noreply@skyfolk.net',
                [self.user.email],
                fail_silently=False,
            )

        return super(CustomLoginForm, self).login(request=request, redirect_url=redirect_url)


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


class AdvancedSearchForm(forms.Form):
    """
    Formulario para la vista avanzada
    que se muestra en la url search-advanced
    """
    all_words = forms.CharField(label="", help_text="Todas estas palabras:", required=False,
                                widget=forms.TextInput(attrs={'placeholder': 'username123, deportes, musica'}))
    word_or_exactly_word = forms.CharField(label="", help_text="Palabra o frase exacta", required=False,
                                           widget=forms.TextInput(attrs={'placeholder': '"Musica de los 90"'}))
    some_words = forms.CharField(label="", help_text="Alguna de estas palabras", required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'perros y/o gatos'}))

    none_words = forms.CharField(label="", help_text="Ninguna de estas palabras", required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'fútbol, baloncesto'}))

    hashtags = forms.CharField(label="", help_text="Estas etiquetas", required=False,
                               widget=forms.TextInput(attrs={'placeholder': '#musica, #cine'}))

    regex_string = forms.CharField(label="", help_text="Esta expresión regular", required=False,
                                   widget=forms.TextInput(
                                       attrs={'placeholder': '"^The": Cadena que comience con "The"'}))


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
        user.save()  # Guardamos el usuario
        user.profile.save()  # Creamos el perfil


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
        fields = ('backImage', 'status',)  # Añadir 'image' si decidimos quitar django-avatar.
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
        fields = ('privacity',)


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
            '<b>Marque esta opción si quiere desactivar su cuenta.</b>'

    def clean_is_active(self):
        is_active = self.cleaned_data["is_active"]
        return is_active


class ThemesForm(forms.Form):
    """
    Formulario para seleccionar los temas
    que interesan a un usuario
    """
    CHOICES = (
        ('D', 'Deportes'),
        ('M', 'Mundo'),
        ('MU', 'Musica'),
        ('C', 'Ciencia'),
        ('L', 'Letras'),
        ('T', 'Tecnología'),
        ('CO', 'Comida'),
        ('MO', 'Motor'),
        ('CON', 'Conocer gente'),
        ('F', 'Fiestas'),
        ('DM', 'De moda'),
        ('VJ', 'Videojuegos'),
        ('FT', 'Fotografía'),
        ('CI', 'Cine'),
        ('A', 'Arte'),
    )

    choices = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
