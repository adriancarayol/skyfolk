from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from user_profile.models import UserProfile


class Publication(models.Model):
    content = models.TextField(blank=False)
    author = models.ForeignKey(UserProfile, related_name='from_publication')
    profile = models.ForeignKey(UserProfile, related_name='to_publication')
    image = models.ImageField(upload_to='publicationimages', verbose_name='Image', blank=True, null=True)
    is_response_from = models.ForeignKey('self', related_name='responses', null=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0, blank=True, null=True)
    user_give_me_like = models.ManyToManyField(User, blank=True)

    # metodos del modelo
    def add_like_pub(self):
        self.likes += 1

    def reduce_like_pub(self):
        self.likes -= 1

    def __str__(self):
        return self.content

#class Hashtag(models.Model):
    #name = models.CharField(max_length=64, unique=True)
    #publicacion = models.ManyToManyField(Publication)

    #class Meta:
        #ordering = ('name',)
        #verbose_name = 'hashtag'
        #verbose_name_plural = 'hashtags'

    #def __unicode__(self):
        #return self.name
