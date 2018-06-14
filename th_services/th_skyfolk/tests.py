# coding: utf-8
from django.test import TestCase
from django.contrib.auth.models import User
from th_services.th_skyfolk.models import Skyfolk
from dash_services.models import TriggerService, UserService, ServicesActivated
from th_services.th_skyfolk.forms import SkyfolkProviderForm, SkyfolkConsumerForm


class SkyfolkTest(TestCase):

    """
        {{ module_name }}Test Model
    """
    def setUp(self):
        """
           create a user
        """
        try:
            self.user = User.objects.get(username='john')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='john', email='john@doe.info', password='doe')

    def create_triggerservice(self, date_created="20130610",
                              description="My first Service", status=True):
        """
           create a TriggerService
        """
        user = self.user

        service_provider = ServicesActivated.objects.create(
            name='ServiceRSS', status=True,
            auth_required=False, description='Service RSS')
        service_consumer = ServicesActivated.objects.create(
            name='Service{{ class_name }}', status=True,
            auth_required=True, description='Service {{ class_name }}')
        provider = UserService.objects.create(user=user,
                                              token="",
                                              name=service_provider)
        consumer = UserService.objects.create(user=user,
                                              token="AZERTY1234",
                                              name=service_consumer)
        return TriggerService.objects.create(provider=provider,
                                             consumer=consumer,
                                             user=user,
                                             date_created=date_created,
                                             description=description,
                                             status=status)

    def create_skyfolk(self):
        """
            Create a {{ class_name }} object related to the trigger object
        """
        trigger = self.create_triggerservice()
        name = '{{ module_name }}'
        status = True
        return Skyfolk.objects.create(trigger=trigger, name=name, status=status)

    def test_skyfolk(self):
        """
           Test if the creation of the {{ module_name }} object looks fine
        """
        d = self.create_skyfolk()
        self.assertTrue(isinstance(d, Skyfolk))
        self.assertEqual(d.show(), "My {{ class_name }} %s" % d.name)

    """
        Form
    """
    # provider
    def test_valid_provider_form(self):
        """
           test if that form is a valid provider one
        """
        d = self.create_skyfolk()
        data = {'name': d.name}
        form = SkyfolkProviderForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_provider_form(self):
        """
           test if that form is not a valid provider one
        """
        form = SkyfolkProviderForm(data={})
        self.assertFalse(form.is_valid())

    # consumer
    def test_valid_consumer_form(self):
        """
           test if that form is a valid consumer one
        """
        d = self.create_skyfolk()
        data = {'name': d.name}
        form = SkyfolkConsumerForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_consumer_form(self):
        """
           test if that form is not a valid consumer one
        """
        form = SkyfolkConsumerForm(data={})
        self.assertFalse(form.is_valid())
