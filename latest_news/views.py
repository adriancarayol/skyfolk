from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from publications.models import Publication
from publications.forms import PublicationForm
from user_profile.forms import SearchForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from timeline.models import Timeline
from user_profile.models import LastUserVisit

class News(TemplateView):
    template_name = "account/base_news.html"

    def get_current_user(self):
        """
        Devuelve el usuario instaciado (logueado)
        """
        return get_object_or_404(get_user_model(),
                username__iexact=self.request.user.username)

    def favourite_users(self):
        """
        Devuelve los 10 perfiles favoritos del usuario
        """
        emitterid = self.get_current_user()
        return LastUserVisit.objects.get_favourite_relation(emitterid=emitterid.profile)

    def get(self, request, *args, **kwargs):
        user_profile = self.get_current_user()
        initial = {'author': user_profile.pk, 'board_owner': user_profile.pk}
        publicationForm = PublicationForm(initial=initial)
        searchForm = SearchForm()
        fav_users = self.favourite_users()
        
        try:
            publications = Publication.objects.get_friend_publications(user_profile.profile)
        except ObjectDoesNotExist:
            publications = None


        return render_to_response(self.template_name, {'publications': publications,
                                                             'publicationSelfForm': publicationForm,
                                                             'searchForm': searchForm,
                                                             'fav_users': fav_users},
                                  context_instance=RequestContext(request))

news_and_updates = login_required(News.as_view())
