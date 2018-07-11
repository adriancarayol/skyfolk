# coding: utf-8

from django import forms
from th_services.th_reddit.models import Reddit
from django.utils.translation import ugettext_lazy as _


class RedditForm(forms.ModelForm):
    """
        form to handle Reddit service
    """

    class Meta:
        model = Reddit
        labels = {
            'share_link': _(u'Share link')
        }
        fields = ['subreddit', 'share_link']


class RedditProviderForm(RedditForm):
    pass


class RedditConsumerForm(RedditForm):
    pass
