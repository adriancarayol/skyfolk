from django.conf import settings
from django.db import models
import six


@six.python_2_unicode_compatible
class Guide(models.Model):
    """
    Describes a guide to be tied to any number of users.
    """
    # The html that should be rendered in a guide.
    html = models.TextField()
    # The type of guide to render. The only guide type currently supported is 'Window.'
    guide_type = models.CharField(max_length=16, choices=(('WINDOW', 'Window'),), default='WINDOW')
    # The name of the guide. Mainly for display purposes.
    guide_name = models.CharField(max_length=64, unique=True)
    # A tag for the given guide. For filtering purposes.
    guide_tag = models.TextField(default='all')
    # An ordering parameter for the guide. To show a guide first, give it a larger guide_importance.
    guide_importance = models.IntegerField(default=0)
    # The creation time of the guide.
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.guide_name)


class GuideInfo(models.Model):
    """
    Ties a guide to a user.
    """
    # The user that should see this guide.
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # The guide that should be shown to the user.
    guide = models.ForeignKey(Guide)
    # Has the guide been seen by a user?
    is_finished = models.BooleanField(default=False)
    # Save the finished time for convenience
    finished_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'guide')
        ordering = ['-guide__guide_importance', 'guide__creation_time']

try:
    Guide.objects.create(
        html='<div>¡Hola!, este es tu perfil. Aquí podrás crear pines y nuevas publicaciones entre otras cosas.</div>',
        guide_name='First guide',
        guide_tag='onboarding',
        guide_importance=5
    )
except:
    pass