from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from api.serializers import UserSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    [API] Permite listar/editar los usuarios.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    [API] Permite listar/editar los grupos
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
