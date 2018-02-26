from django.contrib.auth.models import User
from django.db import transaction
from django.test import TestCase
from neomodel import db, clear_neo4j_database
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from user_profile.node_models import NodeProfile
from user_profile.models import RelationShipProfile, FOLLOWING, BLOCK, \
    LikeProfile, Profile
from publications.models import Publication
from django.core.management import call_command


class UserTestClass(TestCase):
    def setUp(self):
        clear_neo4j_database(db)

    def test_create_object(self):
        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    sql_row = User.objects.create(username="example", password="foo")
                    neo4j_node = NodeProfile(title="example", user_id=sql_row.id).save()
                    raise Exception
        except Exception as e:
            pass

        neo4j_q = NodeProfile.nodes.get_or_none(title="example")
        sql_q = User.objects.filter(username="example").first()

        self.assertIsNone(neo4j_q)
        self.assertIsNone(sql_q)

    def test_create_node(self):
        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    sql_row = User.objects.create(username="example", password="foo")
                    neo4j_node = NodeProfile(title="example", user_id=sql_row.id).save()
        except Exception as e:
            sql_row = None
            neo4j_node = None

        self.assertIsNotNone(sql_row)
        self.assertIsNotNone(neo4j_node)
        self.assertEqual(sql_row.id, neo4j_node.user_id)

    def tearDown(self):
        clear_neo4j_database(db)


class RelationShipTestClass(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        User.objects.create(username="usuario", password="foo")
        User.objects.create(username="usuario2", password="foo")

    def test_create_new_relation_ship(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=FOLLOWING)
        n = NodeProfile.nodes.get(title="usuario")
        m = NodeProfile.nodes.get(title="usuario2")
        self.assertTrue(n.follow.is_connected(m))

    def test_block_user(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=BLOCK)
        n = NodeProfile.nodes.get(title="usuario")
        m = NodeProfile.nodes.get(title="usuario2")
        self.assertTrue(n.bloq.is_connected(m))

    def test_create_new_relationship_blocked_user(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=BLOCK)
        self.assertRaises(IntegrityError,
                          RelationShipProfile.objects.create, to_profile=u2.profile, from_profile=u.profile,
                          type=FOLLOWING)

    def test_create_symmetric_relationship(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=FOLLOWING)
        RelationShipProfile.objects.create(to_profile=u.profile, from_profile=u2.profile, type=FOLLOWING)
        n = NodeProfile.nodes.get(title="usuario")
        m = NodeProfile.nodes.get(title="usuario2")
        self.assertTrue(n.follow.is_connected(m))
        self.assertTrue(m.follow.is_connected(n))

    def tearDown(self):
        clear_neo4j_database(db)


class UserContentTest(TestCase):

    @classmethod
    def setUpTestData(self):
        clear_neo4j_database(db)
        call_command('badgify_sync', 'badges', interactive=False)
        new_user = User.objects.create_user(username="foo", password="foo")
        publications = [Publication.objects.create(author=new_user, content="FOO", board_owner=new_user) for x in
                        range(1, 27)]
        for p in publications:
            p.user_give_me_like.add(new_user)

    def test_get_content(self):
        logged_in = self.client.login(username="foo", password="foo")
        self.assertTrue(logged_in)
        response = self.client.get(reverse('user_profile:salad_user_content'))
        self.assertEqual(response.status_code, 200)

    def test_get_content_no_login(self):
        response = self.client.get(reverse('user_profile:salad_user_content'))
        self.assertEqual(response.status_code, 302)

    def test_get_content_pagination(self):
        logged_in = self.client.login(username="foo", password="foo")
        self.assertTrue(logged_in)
        response = self.client.get(reverse('user_profile:salad_user_content'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mixed']), 25)

    def test_get_content_pagination_page_2(self):
        logged_in = self.client.login(username="foo", password="foo")
        self.assertTrue(logged_in)
        url = '{0}?page={1}'.format(reverse('user_profile:salad_user_content'), 2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mixed']), 1)

    def tearDown(self):
        clear_neo4j_database(db)


class UserLikeTest(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        user_1 = User.objects.create_user(username='foo1', password='foo')
        user_2 = User.objects.create_user(username='foo2', password='foo2')
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(user_1.profile)
        self.assertIsNotNone(user_2.profile)
        self.assertIsNotNone(NodeProfile.nodes.get(title='foo1'))
        self.assertIsNotNone(NodeProfile.nodes.get(title='foo2'))

    def test_like_user(self):
        profile_1 = Profile.objects.get(user__username='foo1')
        profile_2 = Profile.objects.get(user__username='foo2')
        node_1 = NodeProfile.nodes.get(title='foo1')
        node_2 = NodeProfile.nodes.get(title='foo2')
        self.assertIsNotNone(profile_1)
        self.assertIsNotNone(profile_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        like = LikeProfile.objects.create(to_profile=profile_1, from_profile=profile_2)
        self.assertIsNotNone(like)
        self.assertEqual(like.to_profile, profile_1)
        self.assertEqual(like.from_profile, profile_2)
        self.assertFalse(node_1.like.is_connected(node_2))
        self.assertTrue(node_2.like.is_connected(node_1))
