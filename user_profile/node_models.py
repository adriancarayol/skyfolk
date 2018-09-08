import datetime

from django.utils.translation import ugettext_lazy as _
from django_neomodel import DjangoNode
from neomodel import UniqueIdProperty, IntegerProperty, StringProperty, RelationshipTo, BooleanProperty, Relationship, \
    RelationshipFrom, StructuredRel, DateTimeProperty


class TagProfile(DjangoNode):
    title = StringProperty(unique_index=True)
    common = Relationship('TagProfile', 'COMMON')
    user = RelationshipFrom('NodeProfile', 'INTEREST')

    class Meta:
        app_label = 'tag_profile'


class FollowRel(StructuredRel):
    weight = IntegerProperty(default=0)
    created = DateTimeProperty(default=lambda: datetime.datetime.now())

    class Meta:
        app_label = 'django_rel'


class NodeProfile(DjangoNode):
    title = StringProperty(unique_index=True)  # username
    follow = RelationshipTo('NodeProfile', 'FOLLOW', model=FollowRel)  # follow user
    like = RelationshipTo('NodeProfile', 'LIKE')  # like user
    bloq = RelationshipTo('NodeProfile', 'BLOQ')  # bloq user
    is_active = BooleanProperty(default=True, help_text=_(
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'))

    ONLYFOLLOWERS = 'OF'
    ONLYFOLLOWERSANDFOLLOWS = 'OFAF'
    ALL = 'A'
    NOTHING = 'N'
    OPTIONS_PRIVACITY = (
        (ONLYFOLLOWERS, 'OnlyFo'),
        (ONLYFOLLOWERSANDFOLLOWS, 'OnlyFAF'),
        (ALL, 'All'),
        (NOTHING, 'Nothing'),
    )
    privacity = StringProperty(choices=OPTIONS_PRIVACITY, default='A')

    class Meta:
        app_label = 'node_profile'

    def get_followers(self, offset=None, limit=None):
        if limit is not None and offset is not None:

            results, columns = self.cypher(
                "MATCH (a)<-[:FOLLOW]-(b) WHERE id(a)={self} AND b.is_active=true RETURN b ORDER BY b.title SKIP %d LIMIT %d" % (
                    offset, limit))
        else:
            results, columns = self.cypher("MATCH (a)<-[:FOLLOW]-(b) WHERE id(a)={self} AND b.is_active=true RETURN b")

        return [self.inflate(row[0]) for row in results]

    def count_followers(self):
        results, columns = self.cypher(
            "MATCH (a)<-[:FOLLOW]-(b) WHERE id(a)={self} and b.is_active=true RETURN COUNT(b)")
        return results[0][0]

    def get_follows(self, offset=None, limit=None):
        if limit is not None and offset is not None:
            results, columns = self.cypher(
                "MATCH (a)-[:FOLLOW]->(b) WHERE id(a)={self} AND b.is_active=true RETURN b ORDER BY b.title SKIP %d LIMIT %d" % (
                    offset, limit))
        else:
            results, columns = self.cypher("MATCH (a)-[:FOLLOW]->(b) WHERE id(a)={self} AND b.is_active=true RETURN b")
        return [self.inflate(row[0]) for row in results]

    def count_follows(self):
        results, columns = self.cypher(
            "MATCH (a)-[:FOLLOW]->(b) WHERE id(a)={self} and b.is_active=true RETURN COUNT(b)")
        return results[0][0]

    def has_like(self, to_like):
        results, columns = self.cypher(
            "MATCH (a)-[like:LIKE]->(b) WHERE id(a)={self} AND b.title='%s' RETURN like" % to_like)
        return True if len(results) > 0 else False

    def count_likes(self):
        results, columns = self.cypher(
            "MATCH (n:NodeProfile)<-[like:LIKE]-(m:NodeProfile) WHERE id(n)={self} RETURN COUNT(like)")
        return results[0][0]

    def get_like_to_me(self, offset=None, limit=None):
        if offset and limit:
            results, columns = self.cypher(
                "MATCH (n:NodeProfile)<-[like:LIKE]-(m:NodeProfile) WHERE id(n)={self} RETURN m ORDER BY m.title SKIP %d LIMIT %d" % (
                    offset, limit))
        else:
            results, columns = self.cypher(
                "MATCH (n:NodeProfile)<-[like:LIKE]-(m:NodeProfile) WHERE id(n)={self} RETURN m")
        return [self.inflate(row[0]) for row in results]

    def get_favs_users(self, offset=None, limit=None):
        if not limit and not offset:
            results, columns = self.cypher(
                "MATCH (a)-[follow:FOLLOW]->(b) WHERE id(a)={self} and b.is_active=true RETURN b ORDER BY follow.weight DESC LIMIT 6")
        else:
            results, columns = self.cypher(
                "MATCH (a)-[follow:FOLLOW]->(b) WHERE id(a)={self} and b.is_active=true RETURN b ORDER BY follow.weight DESC LIMIT %d" % limit)
        return [self.inflate(row[0]) for row in results]

    def get_favs_followers_users(self):
        results, columns = self.cypher(
            "MATCH (a)<-[follow:FOLLOW]-(b) WHERE id(a)={self} and b.is_active=true RETURN b ORDER BY follow.weight DESC LIMIT 6")
        return [self.inflate(row[0]) for row in results]

    def is_visible(self, user_profile):
        """
        Devuelve si el perfil con id user_id
        es visible por nosotros.
        :param user_profile:
        :return template que determina si el perfil es visible:
        """

        # Si estoy visitando mi propio perfil
        if self.user_id == user_profile.user_id:
            return "all"

        # Si el perfil es privado
        if self.privacity == NodeProfile.NOTHING:
            return "nothing"

        # Si el perfil me bloquea
        if self.bloq.is_connected(user_profile):
            return "block"

        # Recuperamos la relacion de "seguidor"
        try:
            relation_follower = user_profile.follow.is_connected(self)
        except Exception:
            relation_follower = None

        # Si el perfil es seguido y tiene la visiblidad "solo seguidores"
        if self.privacity == NodeProfile.ONLYFOLLOWERS and not relation_follower:
            return "followers"

        # Recuperamos la relacion de "seguir"
        try:
            relation_follow = self.follow.is_connected(user_profile)
        except Exception:
            relation_follow = None

        # Si la privacidad es "seguidores y/o seguidos" y cumple los requisitos
        if self.privacity == NodeProfile.ONLYFOLLOWERSANDFOLLOWS and not \
                (relation_follower or relation_follow):
            return "both"

        # Si el nivel de privacidad es TODOS
        if self.privacity == NodeProfile.ALL:
            return "all"

        return None
