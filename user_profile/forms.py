# encoding:utf-8
import logging
import re

from PIL import Image
from allauth.account.forms import LoginForm
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from ipware.ip import get_real_ip, get_ip

from mailer.mailer import Mailer
from user_profile.models import AuthDevices
from .validators import validate_file_extension

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        auth_browser = forms.CharField(required=False)
        self.fields["auth_browser"] = auth_browser
        self.fields["auth_browser"].widget = forms.HiddenInput()

    def login(self, request, redirect_url=None):
        auth_token_device = self.cleaned_data["auth_browser"]

        ip = get_real_ip(request)

        if ip is not None:
            logger.info("IP: {} del usuario: {}".format(ip, self.user.username))
        else:
            ip = get_ip(request)

        mail = Mailer()

        if auth_token_device:
            try:
                components = auth_token_device.split()
                device, created = AuthDevices.objects.get_or_create(
                    user_profile=self.user, browser_token=components.pop(0)
                )
                if created:
                    device.save()
                    message = "Hemos detectado un nuevo inicio de sesión desde la IP: %s. \n" % ip + ",".join(
                        components
                    ).replace(
                        ",", " "
                    )
                    mail.send_messages(
                        "Skyfolk - Nuevo inicio de sesión..",
                        template="emails/new_login.html",
                        context={"to_user": self.user.username, "message": message},
                        to_emails=(self.user.email,),
                    )
            except (IntegrityError, Exception) as e:
                pass
        else:
            message = "Hemos detectado un nuevo inicio de sesión desde la IP: {}".format(
                ip
            )
            mail.send_messages(
                "Skyfolk - Nuevo inicio de sesión..",
                template="emails/new_login.html",
                context={"to_user": self.user.username, "message": message},
                to_emails=(self.user.email,),
            )

        return super(CustomLoginForm, self).login(
            request=request, redirect_url=redirect_url
        )


class SearchForm(forms.Form):
    """
    Formulario de búsqueda (input)
    que se muestra en el navegador principal de la página web,
    disponible en todas las secciones de la web.
    Como mínimo se debe introducir un caracter para realizar una búsqueda.
    """

    q = forms.CharField(
        label="",
        help_text="",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "¿Que es lo que quieres buscar?",
                "pattern": ".{1,}",
                "required title": "1 character minimum",
                "autocomplete": "off",
            }
        ),
    )
    s = forms.CharField(
        label="", help_text="", required=False, widget=forms.HiddenInput()
    )


class SignupForm(forms.Form):
    """
    Formulario de registro.
    Se usa un validador (alphanumeric) para el nombre y apellido,
    el cual sólo permite introducir letras minúsculas/maýusculas, separadas
    por espacios.
    """

    alphanumeric = RegexValidator(
        r"^(\s*[^\W\d_]+(([\'\-\+\s]\s*[^\W\d_])?[^\W\d_]*)\s*)+$",
        message="Tu nombre/apellido sólo puede contener letras.",
    )
    first_name = forms.CharField(
        label=_("Nombre"),
        min_length=1,
        max_length=35,
        help_text="",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Nombre")}),
        validators=[alphanumeric],
    )
    last_name = forms.CharField(
        label=_("Apellido"),
        min_length=1,
        max_length=35,
        help_text="",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Apellido")}),
        validators=[alphanumeric],
    )

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()  # Guardamos el usuario


class UsernameForm(UserCreationForm):
    username = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")

        reg = re.compile("^[a-zA-Z0-9_]{1,15}$")
        if not reg.match(username):
            if len(username) < 3:
                raise ValidationError(
                    "Se necesitan al menos 3 caracteres para el nombre de usuario."
                )
            if len(username) > 15:
                raise ValidationError(
                    _("El nombre de usuario no puede exceder los 15 caracteres")
                )
            else:
                raise ValidationError(
                    _("El nombre de usuario solo puede tener letras, numeros y _")
                )
        return username

    def clean_password2(self):
        password = self.cleaned_data.get("password2")
        if len(password) < 8:
            raise ValidationError(
                "Se necesitan al menos 8 caracteres para la contraseña."
            )
        return super(UsernameForm, self).clean_password2()


class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"type": "email", "placeholder": _("E-mail address")}
        )
    )
    policy = forms.BooleanField(
        help_text=_(
            'Acepto la <a href="/information/privacy/">politica de privacidad y condiciones de uso</a>.'
        )
    )

    def clean_email(self):
        data = self.cleaned_data["email"]

        if User.objects.filter(email=data).exists():
            error = _("A user is already registered with this e-mail address.")
            raise forms.ValidationError(error)

        return data

    def clean_policy(self):
        data = self.cleaned_data["policy"]

        if not data:
            error = _("Debes aceptar la politica de privacidad para poder registrarte.")
            raise forms.ValidationError(error)
        return data


class UserForm(forms.ModelForm):
    """
    Formulario usado en la configuración del usuario,
    permite cambiar el nombre/apellido del usuario.
    """

    alphanumeric = RegexValidator(
        r"^(\s*[^\W\d_]+(([\'\-\+\s]\s*[^\W\d_])?[^\W\d_]*)\s*)+$",
        message="Tu nombre/apellido sólo puede contener letras.",
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "actual", "maxlength": "30"}),
        validators=[alphanumeric],
        required=False,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "actual", "maxlength": "30"}),
        validators=[alphanumeric],
        required=False,
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name")


class ProfileForm(forms.Form):
    """
    Formulario, que junto con <<UserForm>>, sirven para
    cambiar datos del usuario en configuración.
    <<status>>, sirve para cambiar el estado del usuario
    <<hiddenMenu>>, sirve para escoger que tipo de menú desea visualizar
    en la web.
    """

    status = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "status", "placeholder": "Estado", "maxlength": "20"}
        ),
        required=False,
    )

    backImage = forms.ImageField(
        label="Escoge una imagen.",
        help_text="Elige una imagen de fondo.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_status(self):
        status = self.cleaned_data["status"]

        if len(status) > 20:
            raise forms.ValidationError("El estado no puede exceder de 20 caracteres.")
        return status

    def clean_backImage(self):
        back_image = self.request.FILES.get("image", None)
        if not back_image:
            return None
        if back_image.size > settings.BACK_IMAGE_DEFAULT_SIZE:
            raise forms.ValidationError("La imágen no puede ser mayor a 5MB.")
        if back_image:
            validate_file_extension(back_image)
            trial_image = Image.open(back_image)
            trial_image.verify()
        return back_image


class PrivacityForm(forms.Form):
    """
    Formulario para escoger la privacidad deseada del usuario.
    Se encuentra en configuración, y las opciones son las que
    se describen abajo.
    """

    CHOICES = (
        ("A", "Todos pueden ver mi perfil y mis publicaciones."),
        ("OF", "Sólo mis seguidores pueden ver mi perfil y mis publicaciones."),
        (
            "OFAF",
            "Sólo mis seguidores y aquellas personas que sigo pueden ver mi perfil y mis publicaciones.",
        ),
        ("N", "Nadie puede ver ni mi perfil ni mis publicaciones."),
    )

    privacity = forms.ChoiceField(
        choices=CHOICES, required=True, label="Escoge una opción de privacidad."
    )

    def clean_privacity(self):
        privacity = self.cleaned_data.get("privacity", None)
        if privacity and privacity in dict(PrivacityForm.CHOICES).keys():
            return privacity
        else:
            return "A"


class DeactivateUserForm(forms.ModelForm):
    """
    Formulario para desactivar la cuenta del usuario.
    """

    class Meta:
        model = User
        fields = ["is_active"]

    def __init__(self, *args, **kwargs):
        super(DeactivateUserForm, self).__init__(*args, **kwargs)
        self.fields[
            "is_active"
        ].help_text = "<b>Marque esta opción si quiere desactivar su cuenta.</b>"

    def clean_is_active(self):
        is_active = self.cleaned_data["is_active"]
        return is_active


class ThemesForm(forms.Form):
    """
    Formulario para seleccionar los temas
    que interesan a un usuario
    """

    CHOICES = (
        ("D", "Deportes"),
        ("M", "Mundo"),
        ("MU", "Musica"),
        ("C", "Ciencia"),
        ("L", "Letras"),
        ("T", "Tecnología"),
        ("CO", "Comida"),
        ("MO", "Motor"),
        ("CON", "Conocer gente"),
        ("F", "Fiestas"),
        ("DM", "De moda"),
        ("VJ", "Videojuegos"),
        ("FT", "Fotografía"),
        ("CI", "Cine"),
        ("A", "Arte"),
    )

    choices = forms.MultipleChoiceField(
        choices=CHOICES, widget=forms.CheckboxSelectMultiple(), required=False
    )
