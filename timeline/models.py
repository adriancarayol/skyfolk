from django.db import models
from user_profile.models import UserProfile

class Timeline(models.Model):
    content = models.TextField(blank=False)
    author = models.ForeignKey(UserProfile, related_name='from_author')
    insertion_date = models.DateField(auto_now_add=True)
