from itertools import chain, zip_longest
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from neomodel import db
from user_profile.utils import make_pagination_html
from django.db.models import Q
from publications.forms import PublicationForm
from photologue.models import Photo
from publications.models import Publication
from user_profile.forms import SearchForm
from user_profile.models import Relationship, NodeProfile
from random import shuffle


class News(ListView):
    template_name = "account/base_news.html"
    context_object_name = 'publications'

    def __init__(self, *args, **kwargs):
        super(News, self).__init__(*args, **kwargs)
        self.pagination = None

    def get_affinity_users(self):
        """
        Devuelve los 6 perfiles favoritos del usuario
        """
        n = NodeProfile.nodes.get(user_id=self.request.user.id)
        pk_list = [u.user_id for u in n.get_favs_users()]
        return User.objects.filter(id__in=pk_list)

    def get_recommendation_users(self, offset, limit):
        results, meta = db.cypher_query(
            "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile)<-[:INTEREST]-(u2:NodeProfile) WHERE u1.user_id=%d AND NOT u2.privacity='N' RETURN u2, COUNT(tag) AS score ORDER BY score DESC SKIP %d LIMIT %d" %
            (self.request.user.id, offset, limit))

        users = [NodeProfile.inflate(row[0]) for row in results]
        return users

    def get_queryset(self):
        current_page = int(self.request.GET.get('page', '1')) # page or 1
        limit = 50 * current_page
        offset = limit - 50

        n = NodeProfile.nodes.get(user_id=self.request.user.id)
        pk_list = [x.user_id for x in n.get_favs_users(offset=offset, limit=limit)]

        if len(pk_list) < 50:
            pk_list.extend([u.user_id for u in self.get_recommendation_users(offset, limit)])

        try:
            publications = Publication.objects.filter(
                author__in=pk_list, deleted=False, parent=None).select_related('author', 'shared_publication',
                        'shared_photo_publication', 'parent').prefetch_related('extra_content', 'images', 'videos', 'shared_photo_publication__publication_photo_extra_content', 'shared_publication__extra_content', 'shared_publication__images', 'shared_publication__videos', 'shared_photo_publication__videos', 'shared_photo_publication__images', 'shared_publication__author', 'shared_photo_publication__p_author')[offset:limit]
        except ObjectDoesNotExist:
            publications = []

        try:
            photos = Photo.objects.filter(owner_id__in=pk_list, is_public=True).select_related('owner').prefetch_related('tags').order_by('-date_added')[offset:limit]
        except Photo.DoesNotExist:
            photos = []

        result_list = list(chain.from_iterable([filter(None, zipped) for zipped in zip_longest(publications, photos)]))

        total_pubs = len(result_list)
        total_pages = int(total_pubs / 50)

        if total_pubs % 50 != 0:
            total_pages += 1
            self.pagination = make_pagination_html(current_page, total_pages)
        return result_list

    def get_context_data(self,  **kwargs):
        context = super(News, self).get_context_data(**kwargs)
        context['mix'] = self.get_affinity_users()
        context['follows'] = [u.id for u in self.get_affinity_users()]
        context['pagination'] = self.pagination
        return context


news_and_updates = login_required(News.as_view())
