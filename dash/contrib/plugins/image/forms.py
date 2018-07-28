from django import forms
from django.utils.translation import ugettext_lazy as _

from ....base import DashboardPluginFormBase
from ....widgets import BooleanRadioSelect
from .models import DashImageModel
from .helpers import handle_uploaded_file
from .settings import FIT_METHODS_CHOICES, DEFAULT_FIT_METHOD


__title__ = 'dash.contrib.plugins.image.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2013-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('ImageForm',)


class ImageForm(forms.Form, DashboardPluginFormBase):
    """Image form for `ImagePlugin` plugin."""

    plugin_data_fields = [
        ("title", ""),
        ("image", ""),
    ]

    title = forms.CharField(label=_("Title"), required=True)
    image = forms.ImageField(label=_("Image"), required=True)

    def save_plugin_data(self, request=None):
        """Saving the plugin data and moving the file."""
        image = self.cleaned_data.get('image', None)

        if image:
            im = DashImageModel.objects.create(image=image, user_id=request.user.id)
            self.cleaned_data['image'] = im.id
