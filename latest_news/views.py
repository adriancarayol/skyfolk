from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from publications.models import Publication
from publications.forms import PublicationForm
from user_profile.forms import SearchForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required



class News(TemplateView):
    template_name = "account/base_news.html"

    def get(self, request, *args, **kwargs):
        searchForm = SearchForm()
        publicationForm = PublicationForm()

        username = request.user.username

        user_profile = get_object_or_404(
            get_user_model(), username__iexact=username)

        try:
            publications = Publication.objects.get_authors_publications(user_profile)
        except ObjectDoesNotExist:
            publications = None

        return render_to_response('account/base_news.html', {'publications': publications,
                                                             'publicationForm': publicationForm,
                                                             'searchForm': searchForm},
                                  context_instance=RequestContext(request))

news_and_updates = login_required(News.as_view())
