# from haystack import indexes
#
# from avatar.templatetags.avatar_tags import avatar_url
# from .models import PhotoGroup
# from celery_haystack.indexes import CelerySearchIndex
#
#
# class PhotosIndex(CelerySearchIndex, indexes.Indexable):
#     text = indexes.CharField(
#         document=True, use_template=True,
#         template_name='search/indexes/photos/photos_text.txt')
#
#     author = indexes.CharField(model_attr='owner')
#     avatar = indexes.CharField()
#     title = indexes.CharField(model_attr='title')
#     thumbnail = indexes.CharField(model_attr='thumbnail')
#     url_image = indexes.CharField(model_attr='image')
#     pub_date = indexes.DateTimeField(model_attr='date_added')
#     external_image = indexes.CharField(model_attr='url_image')
#     tags = indexes.MultiValueField()
#     slug = indexes.CharField(model_attr='slug')
#     description = indexes.CharField(model_attr='caption')
#
#     def get_model(self):
#         return PhotoGroup
#
#     def prepare_tags(self, obj):
#         return [tag.slug for tag in obj.tags.all()]
#
#     def prepare_avatar(self, obj):
#         return avatar_url(obj.owner)
