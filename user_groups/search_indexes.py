# from haystack import indexes
# from django.utils import timezone
# from .models import UserGroups
# from celery_haystack.indexes import CelerySearchIndex
#
#
# class GroupIndex(CelerySearchIndex, indexes.Indexable):
#     text = indexes.CharField(
#         document=True, use_template=True,
#         template_name='search/indexes/groups/groups_text.txt')
#
#     owner = indexes.CharField(model_attr='owner')
#     name = indexes.CharField(model_attr='name')
#     description = indexes.CharField(model_attr='description')
#     is_public = indexes.BooleanField(model_attr='is_public')
#     slug = indexes.CharField(model_attr='slug')
#     pub_date = indexes.DateTimeField(model_attr='created')
#     tag = indexes.MultiValueField(indexed=True, stored=True)
#
#     def get_model(self):
#         return UserGroups
#
#     def prepare_tags(self, obj):
#         return [tag.name for tag in obj.tags.all()]
#
#     def index_queryset(self, using=None):
#         return self.get_model().objects.filter(created__lte=timezone.now())
