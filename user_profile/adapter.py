from allauth.account.adapter import DefaultAccountAdapter
from user_profile.models import UserProfile
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adaptador modificado para django-allauth.
    """
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