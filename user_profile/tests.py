from django.contrib.auth.models import User
from django.db import transaction
from django.test import TestCase
from neomodel import db, clear_neo4j_database
from django.db import IntegrityError

from user_profile.node_models import NodeProfile
from user_profile.models import RelationShipProfile, FOLLOWING, BLOCK


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
