import re

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from allauth.exceptions import ImmediateHttpResponse
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from user_profile.models import Profile
from allauth.account.signals import user_signed_up
from invitations.app_settings import app_settings


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        We're trying to solve different use cases:
        - social account already exists, just go on
        - social account has no email or email is unknown, just go on
        - social account's email exists, link social account to existing user
        """

        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email = sociallogin.account.extra_data['email'].lower()
            email_address = EmailAddress.objects.get(email__iexact=email)

        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        user = email_address.user
        sociallogin.connect(request, user)

class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adaptador modificado para django-allauth.
    """

    def clean_username(self, username, **kwargs):
        reg = re.compile('^[a-zA-Z0-9_]{1,15}$')
        if not reg.match(username):
            if len(username) > 15:
                raise ValidationError(_('El nombre de usuario no puede exceder los 15 caracteres'))
            else:
                raise ValidationError(_('El nombre de usuario solo puede tener letras, numeros y _'))
        username = super(MyAccountAdapter, self).clean_username(username=username)
        return username

    def get_login_redirect_url(self, request):
        """
        Devuelve la url a la que se redirige el usuario
        despues de hacer login.
        """

        try:
            user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            raise Http404

        is_first_time_login = user.check_if_first_time_login()

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

    def is_open_for_signup(self, request):
        # For invitations
        if hasattr(request, 'session') and request.session.get(
                'account_verified_email'):
            return True
        elif app_settings.INVITATION_ONLY is True:
            return False
        else:
            return True

    def get_user_signed_up_signal(self):
        # For invitations
        return user_signed_up
