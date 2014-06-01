from django.contrib.auth.models import User
from django.db import models
from allauth.account.models import EmailAddress


class UserProfile(models.Model):
    usuario = models.OneToOneField(User, related_name='profile')

    # Other fields here
    #accepted_eula = models.BooleanField()
    #favorite_animal = models.CharField(max_length=20, default="Dragons.")
    image = models.ImageField(upload_to='userimages', verbose_name='Image')

 
    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

