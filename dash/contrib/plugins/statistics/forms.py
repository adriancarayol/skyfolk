from django import forms
from django.utils.translation import ugettext_lazy as _

from ....base import DashboardPluginFormBase

__title__ = 'dash.contrib.plugins.statistics.forms'
__all__ = (
    'StatisticsForm',
)


class StatisticsForm(forms.Form, DashboardPluginFormBase):
    """StatisticsForm for ``BaseStatisticsPlugin`` plugin."""

    plugin_data_fields = [
        ("title", ""),
    ]

    title = forms.CharField(label=_("Title"), required=True)

    def __init__(self, *args, **kwargs):
        super(StatisticsForm, self).__init__(*args, **kwargs)
