from haystack import indexes

from .models import Publication


class PublicationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/publications/publications_text.txt')

    author = indexes.CharField(model_attr='author')
    content = indexes.CharField(model_attr='content')
    pub_date = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return Publication

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