#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
"""
class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, related_name="profile")
    # añadir campos de perfil
    image = models.ImageField(upload_to='userimages', verbose_name='Image')

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
"""