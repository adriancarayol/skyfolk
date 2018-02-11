from django.db import models
from django.contrib.auth.models import User
from ....models import DashboardEntry


class PollResponse(models.Model):
    user = models.ForeignKey(User)
    poll = models.ForeignKey(DashboardEntry, on_delete=models.CASCADE)
    options = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'poll')

    def save(self, *args, **kwargs):

        if self.poll.plugin_uid.split('_')[0] == 'poll':
            super(PollResponse, self).save(*args, **kwargs)
        else:
            raise Exception("It has to be Poll plugin")
