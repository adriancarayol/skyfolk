# coding: utf-8
from django.conf import settings
from dash_services.service_provider import ServiceProvider
from dash_services.tests.test_main import MainTest
from th_rss.my_rss import ServiceRss


class ServiceProviderTestCase(MainTest):

    def test_get_service(self):
        sp = ServiceProvider()
        sp.load_services(services=settings.TH_SERVICES)
        service = sp.get_service('ServiceRss')
        self.assertIsInstance(service, ServiceRss)
