# coding: utf-8
from django.conf import settings
from skyfolk.service_provider import ServiceProvider
from skyfolk.tests.test_main import MainTest
from th_rss.my_rss import ServiceRss


class ServiceProviderTestCase(MainTest):

    def test_get_service(self):
        sp = ServiceProvider()
        sp.load_services(services=settings.TH_SERVICES)
        service = sp.get_service('ServiceRss')
        self.assertIsInstance(service, ServiceRss)
