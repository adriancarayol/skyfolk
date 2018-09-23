from haystack import indexes
from django.utils import timezone
from .models import Profile
from celery_haystack.indexes import CelerySearchIndex


class ProfileIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/profiles/profiles_text.txt')

    username = indexes.EdgeNgramField(model_attr='user__username')
    firstname = indexes.EdgeNgramField(model_attr='user__first_name')
    lastname = indexes.EdgeNgramField(model_attr='user__last_name')
    pub_date = indexes.DateTimeField(model_attr='user__date_joined')
    tag = indexes.MultiValueField(indexed=True, stored=True)

    def get_model(self):
        return Profile

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(user__date_joined__lte=timezone.now())

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]