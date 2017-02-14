import re

from django.contrib.auth.models import User
from django.db import models

from user_profile.models import UserProfile


class Publication(models.Model):
    content = models.TextField(blank=False)
    author = models.ForeignKey(UserProfile, related_name='from_publication')
    profile = models.ForeignKey(UserProfile, related_name='to_publication')
    image = models.ImageField(upload_to='publicationimages',
                              verbose_name='Image', blank=True, null=True)
    is_response_from = models.ForeignKey('self',
                                         related_name='responses', null=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0, blank=True, null=True)
    hates = models.IntegerField(default=0, blank=True, null=True)
    user_give_me_like = models.ManyToManyField(User, blank=True, related_name='likes_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True, related_name='hates_me')
    parent = models.ForeignKey('self', null=True, related_name='replies')

    # metodos del modelo
    def set_like_pub(self, likes):
        self.likes = likes

    def set_hate_pub(self, hates):
        self.hates = hates

    ''' Menciones para comentario '''

    def getMentions(self):
        menciones = re.findall('\\@[a-zA-Z0-9_]+', self.content)
        for mencion in menciones:
            if User.objects.filter(username=mencion[1:]):
                self.content = self.content.replace(mencion, '<a href="/profile/%s">%s</a>' % (mencion[1:], mencion))

    ''' Tags para comentario '''

    def getHashTags(self):
        hashtags = re.findall('#[a-zA-Z][a-zA-Z0-9_]*', self.content)
        for hashtag in hashtags:
            self.content = self.content.replace(hashtag, '<a href="/search/">%s</a>' % (hashtag))

    def __str__(self):
        return self.content
