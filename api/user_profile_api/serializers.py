from rest_framework import serializers
from django.contrib.auth.models import User
from user_profile.models import Profile, RelationShipProfile
from avatar.templatetags.avatar_tags import avatar_url


class UserSerializer(serializers.ModelSerializer):
	avatar = serializers.SerializerMethodField('get_avatar_user')

	def get_avatar_user(self, obj):
		return avatar_url(obj)

	class Meta:
		model = User
		fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'avatar')
		extra_kwargs = {
            'password': {'write_only': True}
        }


class UserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = Profile
		fields = ('user', 'back_image', 'status', 'is_first_login', 'privacity')


class RelationShipSerializer(serializers.ModelSerializer):

	class Meta:
		model = RelationShipProfile
		fields = ('to_profile', 'from_profile', 'type')
