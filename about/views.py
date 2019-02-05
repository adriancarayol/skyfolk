from el_pagination.views import AjaxListView
from django.views.generic.detail import DetailView

from .models import PublicationBlog


class EntryListView(AjaxListView):
    context_object_name = "publications_blog"
    template_name = "about/publications.html"
    page_template = 'about/entry_list_page.html'

    def get_queryset(self):
        return PublicationBlog.objects.all().order_by('-created')

class PublicationBlogDetailView(DetailView):
    model = PublicationBlog
    template_name = 'about/publication_detail.html'
