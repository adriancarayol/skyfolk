from django.test import TestCase
from .models import Publication

class PublicationTestCase(TestCase):
    def setUp(self):
        Publication.objects.create(content='', author='1')

    def test_parse_content(self):
        pub = Publication.objects.get(author='1')
        self.assertIsNone(pub, pub.content)