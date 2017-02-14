from itertools import chain

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from publications.forms import PublicationForm
from publications.models import Publication
from user_profile.forms import SearchForm
from user_profile.models import AffinityUser, LikeProfile


class News(TemplateView):
    template_name = "account/base_news.html"

    def get_current_user(self):
        """
        Devuelve el usuario instaciado (logueado)
        """
        return get_object_or_404(get_user_model(),
                                 username__iexact=self.request.user.username)

    def get_affinity_users(self):
        """
        Devuelve los 6 perfiles favoritos del usuario
        """
        emitterid = self.get_current_user()
        return AffinityUser.objects.get_favourite_relation(emitterid=emitterid.profile)

    def get_like_users(self):
        """
        Devuelve los 6 perfiles con mas me gusta
        """
        from_like = self.get_current_user()
        return LikeProfile.objects.get_all_likes(from_like=from_like.profile)

    def __mix_queryset(self, affinity, favs):
        """
        Devuelve la lista de usuarios favoritos y
        por afinidad mezclada, sin repetidos
        :param profile => Perfil del que se desea obtener la lista mezclada:
        :return Lista mezlada de usuarios sin repeticiones:
        """
        mixing_list = chain(affinity, favs)
        # sorted(
        # key=lambda user: user.created, reverse=True)

        result = {}
        for user in mixing_list:
            if isinstance(user, AffinityUser):
                if user.receiver_id not in result.keys():
                    result[user.receiver_id] = user.receiver
            else:
                if user.to_like_id not in result.keys():
                    result[user.to_like_id] = user.to_like

        return result.values()

    def get(self, request, *args, **kwargs):
        user_profile = self.get_current_user()
        initial = {'author': user_profile.pk, 'board_owner': user_profile.pk}
        publicationForm = PublicationForm(initial=initial)
        searchForm = SearchForm()
        affinity_users = self.get_affinity_users().values_list('receiver__id', 'receiver__user__username',
                                                               'receiver__user__first_name',
                                                               'receiver__user__last_name')
        print(affinity_users)
        # fav_users = self.get_like_users()
        # mix = self.__mix_queryset(affinity=affinity_users, favs=fav_users)

        # print('LISTA MEZCLADA: {}'.format(self.__mix_queryset(affinity=affinity_users, favs=fav_users)))

        try:
            publications = Publication.objects.get_friend_publications(user_profile.profile)
        except ObjectDoesNotExist:
            publications = None

        context = {'publications': publications,
                   'publicationSelfForm': publicationForm,
                   'searchForm': searchForm,
                   'mix': affinity_users}

        return render(request, self.template_name, context=context)


news_and_updates = login_required(News.as_view())
