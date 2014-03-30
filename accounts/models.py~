#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _ #shorter for ugettext, más info: https://docs.djangoproject.com/en/dev/topics/i18n/translation/#internationalization-in-python-code
from userena.models import UserenaBaseProfile

class MyProfile(UserenaBaseProfile):
    user = models.OneToOneField(User,unique=True, verbose_name=_('user'),related_name='my_profile')
    #firstName = models.CharField(_('nombre'),max_length=20)
    #lastName = models.CharField(_('apellidos'),max_length=50)
    class Meta:
        permissions = (
            ('change_profile', 'Change profile'),
        )

