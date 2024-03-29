import unittest

from django.conf import settings

from .factories import GalleryFactory
from .helpers import PhotologueBaseTest


@unittest.skipUnless(
    "django.contrib.sitemaps" in settings.INSTALLED_APPS,
    "Sitemaps not installed in this project, nothing to test.",
)
class SitemapTest(PhotologueBaseTest):
    urls = "photologue.tests.test_urls"

    def test_get_photo(self):
        """Default test setup contains one photo, this should appear in the sitemap."""
        response = self.client.get("/sitemap.xml")
        self.assertContains(
            response,
            "<url><loc>http://example.com/ptests/photo/landscape/</loc>"
            "<lastmod>2011-12-23</lastmod></url>",
        )

    def test_get_gallery(self):
        """if we add a publications_gallery to the site, we should see both the publications_gallery and
        the photo in the sitemap."""
        self.gallery = GalleryFactory(slug="test-publications_gallery")

        response = self.client.get("/sitemap.xml")
        self.assertContains(
            response,
            "<url><loc>http://example.com/ptests/photo/landscape/</loc>"
            "<lastmod>2011-12-23</lastmod></url>",
        )
        self.assertContains(
            response,
            "<url><loc>http://example.com/ptests/publications_gallery/test-publications_gallery/</loc>"
            "<lastmod>2011-12-23</lastmod></url>",
        )
