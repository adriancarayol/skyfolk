# coding: utf-8

from django import forms
from th_services.th_slack.models import Slack
from django.utils.translation import ugettext_lazy as _


class SlackForm(forms.ModelForm):

    """
        form to handle Slack service
    """

    class Meta:
        model = Slack
        labels = {
            'webhook_url': _('Webhook url')
        }
        fields = ('webhook_url', )


class SlackProviderForm(SlackForm):

    class Meta:
        model = Slack
        labels = {
            'team_id': _('Team id'),
            'slack_token': _('Slack token'),
            'channel': _('Channel')
        }
        fields = ('team_id', 'slack_token', 'channel')


class SlackConsumerForm(SlackForm):

    class Meta:
        model = Slack
        labels = {
            'webhook_url': _('Webhook url')
        }
        fields = ('webhook_url', )
