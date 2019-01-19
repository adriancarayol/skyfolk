from django.contrib.auth.models import User
from django.test import TestCase
from publications_gallery.models import Photo
from .models import PublicationPhoto, ExtraContentPubPhoto


class PublicationGalleryTestCase(TestCase):
    def setUp(self):
        u = User.objects.create(username="example", password="foo")
        p = Photo.objects.create(title="yee", owner=u, image="skyfolk/static/img/nuevo.png")
        PublicationPhoto.objects.create(content='example_content', author=u, board_photo=p)

    def test_parse_content(self):
        pub = PublicationPhoto.objects.get(author__username='example')
        pub.parse_content()
        self.assertIsNotNone(pub, pub.content)

    def test_extra_content(self):
        pub = PublicationPhoto.objects.filter(author__username="example").first()
        e = ExtraContentPubPhoto.objects.create(publication=pub, title="Extra content example")
        self.assertIsNotNone(e)

    def test_like_publication(self):
        pub = PublicationPhoto.objects.filter(author__username="example").first()
        u2 = User.objects.get(username="example")
        pub.user_give_me_like.add(u2)
        self.assertIn(u2, pub.user_give_me_like.all())

    def test_hate_publication(self):
        pub = PublicationPhoto.objects.filter(author__username="example").first()
        u2 = User.objects.get(username="example")
        pub.user_give_me_hate.add(u2)
        self.assertIn(u2, pub.user_give_me_hate.all())

    def test_add_mention(self):
        pub = PublicationPhoto.objects.filter(author__username="example").first()
        content = "Hola @example_2"
        pub.content = content
        pub.parse_mentions()
        pub.save()
        content_parse = 'Hola<a href="/profile/example_2">@example_2</a>'
        self.assertHTMLEqual(content_parse, pub.content)

    def test_delete_extra_content(self):
        pub = PublicationPhoto.objects.filter(author__username="example").first()
        ExtraContentPubPhoto.objects.create(publication=pub, title="Extra content example")
        pub.delete()
        self.assertFalse(ExtraContentPubPhoto.objects.filter(publication=pub).exists())
