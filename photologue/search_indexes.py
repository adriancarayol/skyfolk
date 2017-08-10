from haystack import indexes
from django.contrib.humanize.templatetags.humanize import naturaltime

from .models import Photo


class PhotosIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/photos/photos_text.txt')

    author = indexes.CharField(model_attr='owner')
    title = indexes.CharField(model_attr='title')
    thumbnail = indexes.CharField(model_attr='thumbnail')
    url_image = indexes.CharField(model_attr='image')
    date = indexes.DateTimeField(model_attr='date_added')
    external_image = indexes.CharField(model_attr='url_image')
    tags = indexes.MultiValueField()
    slug = indexes.CharField(model_attr='slug')

    def get_model(self):
        return Photo

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
