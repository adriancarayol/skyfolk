from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.shortcuts import render, get_object_or_404

from user_profile.models import RelationShipProfile, LikeProfile
from user_profile.views.helpers import profile_view_ajax, load_anonymous_profile_publications, fill_profile_dashboard
from loguru import logger


class AnonymousUserProfileView(View):
    def get_ajax(self, request, *args, **kwargs):
        username = kwargs.get('username')

        user_profile = get_object_or_404(
            User.objects.select_related("profile"), username__iexact=username
        )
        return profile_view_ajax(
            request, user_profile
        )

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_ajax(request, *args, **kwargs)

        username = kwargs.get('username')

        user_profile = get_object_or_404(
            User.objects.select_related("profile"), username__iexact=username
        )

        context = {"user_profile": user_profile}

        try:
            num_followers = RelationShipProfile.objects.get_total_followers(
                user_profile.profile.id
            )
        except Exception as e:
            num_followers = 0

        # Recuperamos el numero de contenido multimedia que tiene el perfil
        try:
            multimedia_count = user_profile.profile.get_num_multimedia()
        except ObjectDoesNotExist:
            multimedia_count = 0

        # Recuperamos el numero total de likes
        total_likes = 0
        try:
            total_likes = LikeProfile.objects.filter(to_profile__user__username=username
                                                     ).count()
        except Exception as e:
            logger.info(e)

        context["followers"] = num_followers
        context["n_likes"] = total_likes
        context["multimedia_count"] = multimedia_count
        context["existFollowRequest"] = False
        context["profile_interests"] = user_profile.profile.tags.names()[:10]
        context["profile_interests_total"] = user_profile.profile.tags.all().count()
        context["publications"] = load_anonymous_profile_publications(1, user_profile)
        context["component"] = "publications.js"
        context["friend_page"] = 1

        fill_profile_dashboard(request, user_profile, username, context)

        return render(request, template_name="account/profile.html", context=context)
