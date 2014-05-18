#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    # añadir campos de perfil
    image = models.ImageField(upload_to='userimages', verbose_name='Image')