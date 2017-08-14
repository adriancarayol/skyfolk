import datetime
from haystack import indexes
from django.contrib.auth.models import User


class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/profiles/profiles_text.txt')

    username = indexes.EdgeNgramField(model_attr='username')
    first_name = indexes.EdgeNgramField(model_attr='first_name')
    last_name = indexes.EdgeNgramField(model_attr='last_name')
    # user_fullname = indexes.CharField(model_attr='user')
    # backImage = indexes.CharField(model_attr='backImage')

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    # def index_queryset(self, using=None):
    #     return self.get_model().objects.all()
