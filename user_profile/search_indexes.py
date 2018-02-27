from haystack import indexes
from django.utils import timezone
from .models import Profile


class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/profiles/profiles_text.txt')

    username = indexes.EdgeNgramField(model_attr='user__username')
    firstname = indexes.EdgeNgramField(model_attr='user__first_name')
    lastname = indexes.EdgeNgramField(model_attr='user__last_name')
    pub_date = indexes.DateTimeField(model_attr='user__date_joined')

    def get_model(self):
        return Profile

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(user__date_joined__lte=timezone.now())
