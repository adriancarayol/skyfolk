import re

from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from user_profile.models import UserProfile


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adaptador modificado para django-allauth.
    """

    def clean_username(self, username):
        reg = re.compile('^[a-zA-Z0-9_]{1,15}$')
        if not reg.match(username):
            if len(username) > 15:
                raise ValidationError(_('El nombre de usuario no puede exceder los 15 caracteres'))
            else:
                raise ValidationError(_('El nombre de usuario solo puede tener letras, numeros y _'))
        return username

    def get_login_redirect_url(self, request):
        """
        Devuelve la url a la que se redirige el usuario
        despues de hacer login.
        """
        user = get_object_or_404(get_user_model(), pk=request.user.pk)
        is_first_time_login = UserProfile.objects.check_if_first_time_login(user)

        path = "/profile/{username}/"

        if is_first_time_login:
            print(
                'User {user} is login for the first time'.format(**locals())
            )
            path = "/welcome/{username}"
        else:
            print(
                'User {user} is NOT login for the first time'.format(**locals())
            )

        return path.format(username=request.user.username)
