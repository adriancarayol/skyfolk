from itertools import chain

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Q
from publications.forms import PublicationForm
from publications.models import Publication
from user_profile.forms import SearchForm
from user_profile.models import Relationship, NodeProfile


class News(TemplateView):
    template_name = "account/base_news.html"


    def get_affinity_users(self):
        """
        Devuelve los 6 perfiles favoritos del usuario
        """
        n = NodeProfile.nodes.get(user_id=self.request.user.id)
        return n.get_favs_users()

    def get(self, request, *args, **kwargs):
        initial = {'author': request.user.id, 'board_owner': request.user.id}

        n = NodeProfile.nodes.get(user_id=request.user.id)
        # fav_users = self.get_like_users()
        # mix = self.__mix_queryset(affinity=affinity_users, favs=fav_users)

        # print('LISTA MEZCLADA: {}'.format(self.__mix_queryset(affinity=affinity_users, favs=fav_users)))

        follows = [x.user_id for x in n.follow.match()[:50]]

        try:
            publications = Publication.objects.filter(
                author__in=follows, deleted=False, parent=None)
        except ObjectDoesNotExist:
            publications = None


        context = {'publications': publications,
                   'publicationSelfForm': PublicationForm(initial=initial),
                   'searchForm': SearchForm(),
                   'mix': self.get_affinity_users(),
                   'notifications': request.user.notifications.unread()}

        return render(request, self.template_name, context=context)


news_and_updates = login_required(News.as_view())
