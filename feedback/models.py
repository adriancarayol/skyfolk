from django.db import models


class Feedback(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=64)
    message = models.CharField(max_length=1024)

    def __str__(self):
        return "{} from {}".format(self.message, self.email)
