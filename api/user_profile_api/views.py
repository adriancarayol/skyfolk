from user_profile.models import Profile, RelationShipProfile
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserProfileSerializer, RelationShipSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = Profile.objects.all()


class RelationShipViewSet(viewsets.ModelViewSet):
    serializer_class = RelationShipSerializer
    queryset = RelationShipProfile.objects.all()
