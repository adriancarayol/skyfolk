from itertools import chain, zip_longest
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Q
from publications.forms import PublicationForm
from photologue.models import Photo
from publications.models import Publication
from user_profile.forms import SearchForm
from user_profile.models import Relationship, NodeProfile
from random import shuffle


class News(TemplateView):
    template_name = "account/base_news.html"


    def get_affinity_users(self):
        """
        Devuelve los 6 perfiles favoritos del usuario
        """
        n = NodeProfile.nodes.get(user_id=self.request.user.id)
        pk_list = [u.user_id for u in n.get_favs_users()]
        return User.objects.filter(id__in=pk_list)

    def get_mix_list(self):

        n = NodeProfile.nodes.get(user_id=self.request.user.id)

        follows = [x.user_id for x in n.follow.match()[:50]]

        try:
            publications = Publication.objects.filter(
                author__in=follows, deleted=False, parent=None).select_related('author', 'shared_publication',
                        'shared_photo_publication', 'parent').prefetch_related('extra_content', 'images', 'videos', 'shared_photo_publication__extra_content', 'shared_publication__extra_content', 'shared_publication__images', 'shared_publication__videos', 'shared_photo_publication__videos', 'shared_photo_publication__images', 'shared_publication__author', 'shared_photo_publication__author')
        except ObjectDoesNotExist:
            publications = []

        try:
            photos = Photo.objects.filter(owner_id=self.request.user.id, is_public=True).select_related('owner').prefetch_related('tags')
        except Photo.DoesNotExist:
            photos = []

        result_list = list(chain.from_iterable([filter(None, zipped) for zipped in zip_longest(publications, photos)]))
        return follows, result_list

    def get(self, request, *args, **kwargs):

        follows, result_list= self.get_mix_list()

        context = {'publications': result_list,
                   'searchForm': SearchForm(),
                   'follows': follows,
                   'mix': self.get_affinity_users(),}

        return render(request, self.template_name, context=context)


news_and_updates = login_required(News.as_view())
