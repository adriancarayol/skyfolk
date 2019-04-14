from django.contrib.auth.models import User
from django.db import models


class UserRank(models.Model):
    reached_with = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, verbose_name="users", blank=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)

    class Meta:
        unique_together = ("name", "reached_with")

    def __repr__(self):
        return "<UserRank reached_with={} created={} name={} description={}".format(
            self.reached_with, self.created, self.name, self.description
        )

    def __str__(self):
        return "{}: {}".format(self.name, self.description)
