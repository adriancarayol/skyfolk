from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from publications.forms import PublicationForm, PublicationEdit, SharedPublicationForm
from user_profile.constants import BLOCK, FOLLOWING
from user_profile.models import Profile, LikeProfile, RelationShipProfile, Request
from user_profile.views.helpers import profile_view_ajax, load_profile_publications, fill_profile_dashboard
from loguru import logger
from braces.views import AjaxResponseMixin


class AuthenticatedUserProfileView(View, LoginRequiredMixin, AjaxResponseMixin):
    template_name = 'account/profile.html'

    def get_ajax(self, request, *args, **kwargs):
        username = kwargs.get('username')

        user_profile = get_object_or_404(
            User.objects.select_related("profile"), username__iexact=username
        )
        return profile_view_ajax(
            request, user_profile, node_profile=user_profile.profile
        )

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_ajax(request, *args, **kwargs)

        username = kwargs.get('username')
        user = request.user
        template = self.template_name

        try:
            request_profile = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist as e:
            logger.info('Profile: {} not exists. {}'.format(user, e))
            raise Http404

        user_profile = get_object_or_404(
            User.objects.select_related("profile"), username__iexact=username
        )
        context = {}

        privacity = user_profile.profile.is_visible(request_profile)

        context["user_profile"] = user_profile
        context["privacity"] = privacity

        if user.username != username:
            try:
                liked = LikeProfile.objects.filter(
                    to_profile__user__username=username, from_profile__user=user
                ).exists()
            except Exception:
                liked = False
        else:
            liked = False

        # Recuperamos el numero total de likes
        total_likes = 0
        try:
            total_likes = LikeProfile.objects.filter(
                to_profile__user__username=username
            ).count()
        except Exception as e:
            logger.info(e)

        # Comprobamos si el perfil esta bloqueado
        isBlocked = False
        if user.username != username:
            try:
                isBlocked = RelationShipProfile.objects.filter(
                    from_profile=request_profile, to_profile=user_profile.profile, type=BLOCK
                ).exists()
            except Exception as e:
                pass

        # Comprobamos si el perfil es seguidor
        isFollower = False
        if user.username != username:
            try:
                isFollower = RelationShipProfile.objects.filter(
                    from_profile=user_profile.profile, to_profile=request_profile, type=FOLLOWING
                ).exists()
            except Exception:
                pass
        # Comprobamos si el perfil es seguido
        isFollow = False
        if user.username != username:
            try:
                isFollow = RelationShipProfile.objects.filter(
                    from_profile=request_profile, to_profile=user_profile.profile, type=FOLLOWING
                ).exists()
            except Exception:
                pass
        # Comprobamos si existe una peticion de seguimiento
        try:
            friend_request = Request.objects.get_follow_request(
                from_profile=user.id, to_profile=user_profile.id
            )
        except ObjectDoesNotExist:
            friend_request = None

        # Cuando no tenemos permisos suficientes para ver nada del perfil
        if privacity == "nothing":
            context["isBlocked"] = isBlocked
            context["liked"] = liked
            context["isFollower"] = isFollower
            context["isFriend"] = isFollow
            context["existFollowRequest"] = True if friend_request else False
            template = "account/privacity/private_profile.html"
            return render(request, template, context)
        elif RelationShipProfile.objects.filter(
                from_profile=user_profile.profile, to_profile=request_profile, type=BLOCK
        ):
            template = "account/privacity/block_profile.html"
            context["isBlocked"] = isBlocked
            context["liked"] = liked
            return render(request, template, context)

        # Recuperamos el numero de seguidores
        try:
            num_followers = RelationShipProfile.objects.get_total_followers(
                user_profile.profile.id
            )
        except Exception as e:
            num_followers = 0

        # Recuperamos el numero de contenido multimedia que tiene el perfil
        try:
            if user.username == username:
                multimedia_count = user_profile.profile.get_total_num_multimedia()
            else:
                multimedia_count = user_profile.profile.get_num_multimedia()
        except ObjectDoesNotExist:
            multimedia_count = 0

        context["liked"] = liked
        context["n_likes"] = total_likes
        context["followers"] = num_followers
        context["isBlocked"] = isBlocked
        context["isFollower"] = isFollower
        context["isFriend"] = isFollow
        context["multimedia_count"] = multimedia_count
        context["existFollowRequest"] = True if friend_request else False

        context["profile_interests"] = user_profile.profile.tags.names()[:10]
        context["profile_interests_total"] = user_profile.profile.tags.all().count()

        if privacity == "followers" or privacity == "both":
            template = "account/privacity/need_confirmation_profile.html"
            return render(request, template, context)

        context["publicationForm"] = PublicationForm()
        context["publication_edit"] = PublicationEdit()
        context["publication_shared"] = SharedPublicationForm()
        context["publications"] = load_profile_publications(request, 1, user_profile)
        context["component"] = "publications.js"
        context["friend_page"] = 1

        fill_profile_dashboard(request, user_profile, username, context)

        return render(request, template_name=template, context=context)
