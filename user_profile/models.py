from django.contrib.auth.models import User
from django.db import models
from allauth.account.models import EmailAddress
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _


RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_BLOCKED = 2
RELATIONSHIP_FRIEND = 3
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
    (RELATIONSHIP_FRIEND, 'Friend'),
)


REQUEST_FRIEND = 1
REQUEST_STATUSES = (
    (REQUEST_FRIEND, 'Friend'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='profile')
    
    # Other fields here
    #accepted_eula = models.BooleanField()
    #favorite_animal = models.CharField(max_length=20, default="Dragons.")
    image = models.ImageField(upload_to='userimages', verbose_name='Image',blank=True, null=True)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to+')
    likeprofiles = models.ManyToManyField('self', through='LikeProfile', symmetrical=False, related_name='likesToMe')
    requests = models.ManyToManyField('self', through='Request', symmetrical=False, related_name='requestsToMe')

    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    """
    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False
    """



    #Methods of relationships between users
    def add_relationship(self, person, status, symm=False):
        relationship, created = Relationship.objects.get_or_create(from_person=self, to_person=person, status=status)
        if symm:
            # avoid recursion by passing 'symm=False'
            person.add_relationship(self, status, False)
        return relationship

    def remove_relationship(self, person, status, symm=False):
        Relationship.objects.filter(from_person=self, to_person=person, status=status).delete()
        if symm:
            # avoid recursion by passing 'symm=False'
            person.remove_relationship(self, status, False)

    def get_relationships(self, status):
        return self.relationships.filter(
            to_people__status=status, 
            to_people__from_person=self)

    def get_related_to(self, status):
        return self.related_to.filter(
            from_people__status=status, 
            from_people__to_person=self)

    def get_following(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWING)

    def get_followers(self):
        return self.get_related_to(RELATIONSHIP_FOLLOWING)

    def get_friends(self):
        return self.get_relationships(RELATIONSHIP_FRIEND).order_by('id')

    def get_blockeds(self):
        return self.get_related_to(RELATIONSHIP_BLOCKED)

    
    #methods likes
    def add_like(self, profile):
        like, created = LikeProfile.objects.get_or_create(from_like=self, to_like=profile)
        return like

    def remove_like(self, profile):
        LikeProfile.objects.filter(from_like=self, to_like=profile).delete()

    def get_likes(self):
        return self.likeprofiles.filter(to_likeprofile__from_like=self)

    def has_like(self, profile):
        return LikeProfile.objects.get(from_like=self, to_like=profile)


    #methods friends
    def add_friend(self, profile):
        return self.add_relationship(profile, RELATIONSHIP_FRIEND, True) #mas adelante cambiar aqui True por False

    def is_friend(self, profile):
        return Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FRIEND)

    def get_friends_top4(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).order_by('id')[0:4]

    def add_friend_request(self, profile):
        obj, created = Request.objects.get_or_create(emitter=self, receiver=profile, status=REQUEST_FRIEND)
        return obj

    def get_friend_request(self, profile):
        return Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FRIEND)

"""
    def get_friends_next4(self, next):
        n = next * 4
        return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).order_by('id')[n-4:n]
"""




User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])





class Relationship(models.Model):
    from_person = models.ForeignKey(UserProfile, related_name='from_people')
    to_person = models.ForeignKey(UserProfile, related_name='to_people')
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_person', 'to_person', 'status')

class LikeProfile(models.Model):
    from_like = models.ForeignKey(UserProfile, related_name='from_likeprofile')
    to_like = models.ForeignKey(UserProfile, related_name='to_likeprofile')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_like', 'to_like')


class Request(models.Model):
    emitter = models.ForeignKey(UserProfile, related_name='from_request')
    receiver = models.ForeignKey(UserProfile, related_name='to_request')
    status = models.IntegerField(choices=REQUEST_STATUSES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('emitter', 'receiver', 'status')