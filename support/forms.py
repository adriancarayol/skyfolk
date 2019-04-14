# encoding:utf-8
from django import forms
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from .models import SupportPasswordModel


class SupportPasswordForm(forms.ModelForm):
    """
    Formulario para enviar un nuevo ticket
    a un problema relacionado con el password
    de un usuario.
    """

    class Meta:
        model = SupportPasswordModel
        exclude = ("user",)

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "cols": 80,
                    "rows": 20,
                    "class": "materialize-textarea",
                    "placeholder": "Describe tu problema aqui",
                }
            ),
            "title": forms.TextInput(
                attrs={"placeholder": "Pon un titulo a tu problema"}
            ),
        }
        labels = {"description": _("Descripcion del problema"), "title": _("Titulo")}
        error_messages = {
            "username_or_email": {
                "wrong_account": _(
                    "No hay ninguna cuenta asociada a ese nombre de usuario o email"
                )
            }
        }

    username_or_email = forms.CharField(
        max_length=128,
        required=True,
        label=_("Nombre de usuario o email de la cuenta"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Introduce el nombre de usuario o email de tu cuenta")
            }
        ),
    )

    def send_email(self, title, description, email):
        send_mail(
            "[Skyfolk] - Ayuda y soporte.",
            "Ha solicitado ayuda al soporte de Skyfolk con el siguiente contenido: \n Titulo: %s \n Descripcion: %s"
            % (title, description),
            "noreply@skyfolk.net",
            [email],
            fail_silently=False,
        )

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data["username_or_email"]

        if not username_or_email:
            raise forms.ValidationError(
                _("No hay ninguna cuenta asociada a ese nombre de usuario o email")
            )
        return username_or_email
