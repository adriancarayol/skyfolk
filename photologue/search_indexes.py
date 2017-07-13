from haystack import indexes

from .models import Photo


class PhotosIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/photos/photos_text.txt')

    author = indexes.CharField(model_attr='owner')
    title = indexes.CharField(model_attr='title')
    thumbnail = indexes.CharField(model_attr='thumbnail')
    url_image = indexes.CharField(model_attr='image')
    date_added = indexes.CharField(model_attr='date_added')

    def get_model(self):
        return Photo