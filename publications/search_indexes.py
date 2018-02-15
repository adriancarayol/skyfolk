import datetime
from haystack import indexes
from .models import Publication


class PublicationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/publications/publications_text.txt')

    author = indexes.CharField(model_attr='author')
    content = indexes.CharField(model_attr='content')
    pub_date = indexes.DateTimeField(model_attr='created')
    tag = indexes.MultiValueField(indexed=True, stored=True)
    delete = indexes.BooleanField(model_attr='deleted')

    def get_model(self):
        return Publication

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(created__lte=datetime.datetime.now())

        # def index_queryset(self, using=None):
    #     return self.get_model().objects.all()


# class VideosIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(
#         document=True, use_template=True,
#         template_name='search/indexes/publications/photos_text.txt')
#
#     author = indexes.CharField(model_attr='author')
#     video = indexes.CharField(model_attr='video')
#
#     def get_model(self):
#         return PublicationVideo
