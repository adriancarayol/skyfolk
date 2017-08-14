import datetime
from haystack import indexes
from .models import Profile


class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/profiles/profiles_text.txt')

    username = indexes.EdgeNgramField(model_attr='user__username')
    firstname = indexes.EdgeNgramField(model_attr='user__first_name')
    lastname = indexes.EdgeNgramField(model_attr='user__last_name')
    back_image = indexes.CharField(model_attr='back_image')
    # user_fullname = indexes.CharField(model_attr='user')
    # backImage = indexes.CharField(model_attr='backImage')

    def get_model(self):
        return Profile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    # def index_queryset(self, using=None):
    #     return self.get_model().objects.all()
