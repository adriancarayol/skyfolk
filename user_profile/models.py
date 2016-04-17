import publications
import timeline
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# from publications.models import Publication
# from _overlapped import NULL
RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_BLOCKED = 2
RELATIONSHIP_FRIEND = 3
RELATIONSHIP_FOLLOWER = 4
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
    (RELATIONSHIP_FRIEND, 'Friend'),
    (RELATIONSHIP_FOLLOWER, 'Follower'),
)

REQUEST_FRIEND = 1
REQUEST_FOLLOWING = 2
REQUEST_FOLLOWER = 3
REQUEST_BLOCKED = 4
REQUEST_STATUSES = (
    (REQUEST_FRIEND, 'Friend'),
    (REQUEST_FOLLOWING, 'Following'),
    (REQUEST_FOLLOWER, 'Follower'),
    (REQUEST_FRIEND, 'Friend'),
)


def uploadAvatarPath(instance, filename):
    return '%s/avatar/%s' % (instance.user.username, filename)


def uploadBackImagePath(instance, filename):
    return '%s/backImage/%s' % (instance.user.username, filename)


class UserProfile(models.Model):
    PIN_LENGTH = 9

    user = models.OneToOneField(User, unique=True, related_name='profile')

    # Other fields here
    # accepted_eula = models.BooleanField()
    # favorite_animal = models.CharField(max_length=20, default="Dragons.")
    backImage = models.ImageField(upload_to=uploadBackImagePath, verbose_name='BackImage', blank=True, null=True)
    image = models.ImageField(upload_to=uploadAvatarPath, verbose_name='Image', blank=True, null=True)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to')
    likeprofiles = models.ManyToManyField('self', through='LikeProfile', symmetrical=False, related_name='likesToMe')
    requests = models.ManyToManyField('self', through='Request', symmetrical=False, related_name='requestsToMe')
    publications = models.ManyToManyField('self', through='publications.Publication', symmetrical=False,
                                          related_name='publications_to')
    timeline = models.ManyToManyField('self', through='timeline.Timeline', symmetrical=False,
                                      related_name='timeline_to')
    status = models.CharField(max_length=20, null=True, verbose_name='estado')
    ultimosUsuariosVisitados = models.ManyToManyField('self')  # Lista de ultimos usuarios visitados.
    firstLogin = models.BooleanField(
        default=False)  # Para ver si el usuario ha realizado su primer login en la web, y por lo tanto, mostrar configuracion inicial.
    hiddenMenu = models.BooleanField(
        default=True)  # Para que el usuario decida que menu le gustaria tener, si el oculto o el estático.

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

    def save(self, *args, **kwargs):
        # delete old image when replacing by updating the file
        try:
            this = UserProfile.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case
        super(UserProfile, self).save(*args, **kwargs)

    # Methods of relationships between users
    def add_relationship(self, person, status, symm=False):
        print('>>>>>>> add_relationship')
        relationship, created = Relationship.objects.get_or_create(from_person=self, to_person=person, status=status)
        print('>>>>>>> created')
        print(created)
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

    # Methods of timeline

    def getTimelineToMe(self):
        return self.timeline_to.filter(
            from_timeline__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                'from_timeline__id',
                                                'from_timeline__content', 'from_timeline__insertion_date').order_by(
            'from_timeline__insertion_date').reverse()

    def remove_timeline(self, timeline_id):
        timeline.models.Timeline.objects.get(pk=timeline_id).delete()

    # Methods of publications


    def get_publication(self, publicationid):
        return publications.models.Publication.objects.get(pk=publicationid)


    def remove_publication(self, publicationid):
        publications.models.Publication.objects.get(pk=publicationid).delete()

    def get_publicationsToMe(self):
        return self.publications_to.filter(
            from_publication__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                   'from_publication__id',
                                                   'from_publication__content', 'from_publication__created',
                                                   'from_publication__likes', 'user__profile__image',
                                                   'from_publication__hates', 'from_publication__replies').order_by(
            'from_publication__created').reverse()

    def get_publicationsToMeTop15(self):
        return self.publications_to.filter(
            from_publication__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                   'from_publication__id',
                                                   'from_publication__content', 'from_publication__created',
                                                   'from_publication__likes',
                                                   'user__profile__image').order_by(
            'from_publication__created').reverse()[0:15]

    def get_myPublications(self):
        return self.publications.filter(
            to_publication__author=self).values('user__username', 'to_publication__profile', 'user__first_name',
                                                'user__last_name',
                                                'from_publication__id', 'to_publication__content',
                                                'to_publication__created', 'to_publication__likes',
                                                'to_publication__user_give_me_like').reverse()

    # Obtener seguidos
    def get_following(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWING).values('user__id', 'user__username', 'user__first_name',
                                                                     'user__last_name', 'user__profile__image',
                                                                     'user__profile__backImage').order_by('id')

    # Obtener seguidores
    def get_followers(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWER).values('user__id', 'user__username', 'user__first_name',
                                                                    'user__last_name', 'user__profile__image',
                                                                    'user__profile__backImage').order_by('id')

    def get_friends(self):
        return self.get_relationships(RELATIONSHIP_FRIEND).values('user__id', 'user__username', 'user__first_name',
                                                                  'user__last_name', 'user__profile__image',
                                                                  'user__profile__backImage').order_by('id')

    def get_blockeds(self):
        return self.get_related_to(RELATIONSHIP_BLOCKED)

    # methods likes
    def add_like(self, profile):
        like, created = LikeProfile.objects.get_or_create(from_like=self, to_like=profile)
        return like

    def remove_like(self, profile):
        LikeProfile.objects.filter(from_like=self, to_like=profile).delete()

    def get_likes(self):
        return self.likeprofiles.filter(to_likeprofile__from_like=self)

    def has_like(self, profile):
        return LikeProfile.objects.get(from_like=self, to_like=profile)

    # methods following

    def is_follow(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FOLLOWING):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # Add following
    def add_follow(self, profile):
        print('>>>>>> add_follow')
        return self.add_relationship(profile, RELATIONSHIP_FOLLOWING,
                                     False)

    def get_follow_top12(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FOLLOWING, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')[0:12]

    def get_follow_objectlist(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FOLLOWING, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')

    def add_follow_request(self, profile):
        obj, created = Request.objects.get_or_create(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)
        return obj

    def get_follow_request(self, profile):
        return Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)

    def get_received_follow_requests(self):
        return self.requestsToMe.filter(from_request__status=2, from_request__receiver=self)

    def remove_received_follow_request(self, profile):
        Request.objects.filter(emitter=profile, receiver=self, status=REQUEST_FOLLOWING).delete()

    # methods followers
    def is_follower(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FOLLOWER):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # add follower
    def add_follower(self, profile):
        print('>>>>> add_follower')
        return self.add_relationship(profile, RELATIONSHIP_FOLLOWER,
                                     False)

    # methods friends
    def is_friend(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FRIEND):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    def add_friend(self, profile):
        print('>>>>>>> add_friend')
        return self.add_relationship(profile, RELATIONSHIP_FRIEND,
                                     True)  # mas adelante cambiar aqui True por False
        # para diferenciar seguidores de seguidos.

    def get_friends_top12(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')[0:12]

    def get_friends_objectlist(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')

    def add_friend_request(self, profile):
        obj, created = Request.objects.get_or_create(emitter=self, receiver=profile, status=REQUEST_FRIEND)
        return obj

    def get_friend_request(self, profile):
        return Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FRIEND)

    def get_received_friends_requests(self):
        return self.requestsToMe.filter(from_request__status=1, from_request__receiver=self)

    def remove_received_friend_request(self, profile):
        Request.objects.filter(emitter=profile, receiver=self, status=REQUEST_FRIEND).delete()

    """
        def get_friends_next4(self, next):
            n = next * 4
            return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).order_by('id')[n-4:n]
    """

    @property
    def pin(self):
        # PIN format: pk + token + diff
        print('>>>>>>> get_pin()')
        str_pk = str(self.pk)
        length = len(str_pk)
        if length < self.PIN_LENGTH:
            diff = self.PIN_LENGTH - length - 1
            # the value used as pickle needs generate a number with 8 digits as minimal length
            pickle = 87654321.13
            if length >= 3 and length < 6:
                pickle = 876543.13
            elif length >= 6 and length < 9:
                pickle = 8765.13
            token = str(self.pk * pickle).replace('.', '')[-diff:]
            str_pk = '{}{}{}'.format(str_pk, token, diff)
            return str_pk
        else:
            return str_pk

    def get_pk_for_pin(pin):
        if len(pin) == 9:
            diff = int(pin[-1:])
            return pin[:-(diff + 1)]
        return None


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
