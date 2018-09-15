from django.contrib.auth.models import User
from rest_framework import serializers
from django.templatetags.static import static

from avatar.templatetags.avatar_tags import avatar_url


class UserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    avatar = serializers.SerializerMethodField('get_avatar_user')
    back_image = serializers.SerializerMethodField('get_back_image_user')

    def get_avatar_user(self, obj):
        return avatar_url(obj)

    def get_back_image_user(self, obj):
        default_back = static('dist/img/nuevo_back.jpg')
        return obj.profile.back_image.url if obj.profile.back_image else default_back

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'avatar', 'back_image')
