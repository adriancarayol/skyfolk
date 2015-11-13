from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
from user_profile.models import UserProfile


# Create your models here.
class Publication(models.Model):
    content = models.TextField(blank=False)
    writer = models.ForeignKey(UserProfile, related_name='from_publication')
    profile = models.ForeignKey(UserProfile, related_name='to_publication')
    image = models.ImageField(upload_to='publicationimages', verbose_name='Image', blank=True, null=True)
    is_response_from = models.ForeignKey('self', related_name='responses', null=True)
    created = models.DateTimeField(auto_now_add=True)
    mlikes = models.CharField(blank=True, default=0, max_length=3)
    user_give_me_like = models.ManyToManyField(User, blank=True)

    def add_like_pub(self):
        _numLikes = int(self.mlikes)
        _numLikes += 1
        self.mlikes = str(_numLikes)

    def reduce_like_pub(self):
        _numLikes = int(self.mlikes)
        _numLikes -= 1
        self.mlikes = str(_numLikes)
