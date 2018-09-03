from haystack import indexes
from django.utils import timezone
from avatar.templatetags.avatar_tags import avatar_url
from .models import Photo, Video


class PhotosIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/photos/photos_text.txt')

    author = indexes.CharField(model_attr='owner')
    avatar = indexes.CharField()
    title = indexes.CharField(model_attr='title')
    thumbnail = indexes.CharField(model_attr='thumbnail')
    url_image = indexes.CharField(model_attr='image')
    pub_date = indexes.DateTimeField(model_attr='date_added')
    external_image = indexes.CharField(model_attr='url_image')
    tags = indexes.MultiValueField()
    slug = indexes.CharField(model_attr='slug')
    description = indexes.CharField(model_attr='caption')

    def get_model(self):
        return Photo

    def prepare_tags(self, obj):
        return [tag.slug for tag in obj.tags.all()]

    def prepare_avatar(self, obj):
        return avatar_url(obj.owner)

    def prepare_thumbnail(self, obj):
        return obj.thumbnail.url

    def prepare_url_image(self, obj):
        return obj.image.url

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(date_added__lte=timezone.now())


class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True,
        template_name='search/indexes/videos/videos_text.txt')

    author = indexes.CharField(model_attr='owner')
    avatar = indexes.CharField()
    name = indexes.CharField(model_attr='name')
    thumbnail = indexes.CharField(model_attr='thumbnail')
    video = indexes.CharField(model_attr='video')
    pub_date = indexes.DateTimeField(model_attr='date_added')
    tags = indexes.MultiValueField()
    slug = indexes.CharField(model_attr='slug')
    description = indexes.CharField(model_attr='caption')

    def get_model(self):
        return Video

    def prepare_tags(self, obj):
        return [tag.slug for tag in obj.tags.all()]

    def prepare_avatar(self, obj):
        return avatar_url(obj.owner)

    def prepare_thumbnail(self, obj):
        return obj.thumbnail.url

    def prepare_video(self, obj):
        return obj.video.url

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(date_added__lte=timezone.now())
