from django.db.models import Sum
from django_elasticsearch_dsl import DocType, Index, fields
from taggit.models import TaggedItem
from django.contrib.auth.models import User

from badgify.models import Award, Badge
from user_profile.models import Profile, LikeProfile, RelationShipProfile
from user_profile.constants import FOLLOWING
from photologue.models import Video, Photo

user_profile = Index('user_profiles')
user_profile.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@user_profile.doc_type
class ProfileDocument(DocType):
    class Meta:
        model = Profile

        fields = [
            'back_image',
            'status',
        ]
        related_models = [User, TaggedItem, RelationShipProfile, LikeProfile, Photo, Video, Award, Badge]

    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'username': fields.StringField(),
        'first_name': fields.StringField(),
        'last_name': fields.StringField()
    })
    tags = fields.NestedField(properties={
        'slug': fields.StringField(),
        'name': fields.StringField()
    })
    likes_count = fields.IntegerField()
    followers_count = fields.IntegerField()
    photos_count = fields.IntegerField()
    videos_count = fields.IntegerField()
    exp_count = fields.IntegerField()

    def prepare_likes_count(self, instance):
        return LikeProfile.objects.filter(to_profile=instance).count()

    def prepare_followers_count(self, instance):
        return RelationShipProfile.objects.filter(to_profile=instance, type=FOLLOWING).count()

    def prepare_photos_count(self, instance):
        return Photo.objects.filter(owner_id=instance.user.id).count()

    def prepare_videos_count(self, instance):
        return Video.objects.filter(owner_id=instance.user.id).count()

    def prepare_exp_count(self, instance):
        awards = Award.objects.filter(user__profile__id=instance.id).values('user__profile__id').annotate(
            exp_count=Sum('badge__points'))
        return next(iter([exp['exp_count'] for exp in awards] or []), 0)

    def get_queryset(self):
        return super(ProfileDocument, self).get_queryset().select_related(
            'user'
        ).prefetch_related('tags')

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return Profile.objects.filter(user_id=related_instance.id)
