from django.db import models
from django.contrib.auth.models import User
from user_profile.models import UserProfile
from publications.models import Publication

class Timeline(models.Model):
    publication = models.ForeignKey(Publication, blank=True, null=True, related_name='publication_to_timeline')
    content = models.TextField(blank=False)
    author = models.ForeignKey(UserProfile, related_name='from_timeline')
    profile = models.ForeignKey(UserProfile, related_name='to_timeline')
    insertion_date = models.DateField(auto_now_add=True)
    users_add_me = models.ManyToManyField(User, blank=True, related_name='users_add_me')
    count_of_users = models.IntegerField(default=0, blank=True, null=True)

    def set_users(self, num):
        self.count_of_users = num
    # Mostrar contenido en formato string.
    def __str__(self):
        return self.content
