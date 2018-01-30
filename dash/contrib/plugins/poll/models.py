from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Poll(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True)


class PollResponse(models.Model):
    user = models.ForeignKey(User)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    options = models.BooleanField(default=False)
