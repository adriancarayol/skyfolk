__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('BaseImagePlugin',)

from django.utils.translation import ugettext_lazy as _

from dash.base import BaseDashboardPlugin
from dash.contrib.plugins.image.forms import ImageForm
from dash.contrib.plugins.image.helpers import delete_file, clone_file
from dash.factory import plugin_factory

# *****************************************************************************
# ***************************** Base Image plugin *****************************
# *****************************************************************************
class BaseImagePlugin(BaseDashboardPlugin):
    """
    Base image plugin.
    """
    name = _("Image")
    group = _("Image")
    form = ImageForm
    html_classes = ['pictonic']

    def delete_plugin_data(self):
        """
        Deletes uploaded file.
        """
        delete_file(self.data.image)

    def clone_plugin_data(self, dashboard_entry):
        """
        Clone plugin data, which means we make a copy of the original image.

        TODO: Perhaps rely more on data of `dashboard_entry`?
        """
        cloned_image = clone_file(self.data.image, relative_path=True)
        return self.get_cloned_plugin_data(update={'image': cloned_image})


# *****************************************************************************
# ********** Generating and registering the plugins using factory *************
# *****************************************************************************
sizes = (
    (1, 1),
    (1, 2),
    (2, 1),
    (2, 2),
    (2, 3),
    (3, 2),
    (3, 3),
    (3, 4),
    (4, 3),
    (4, 4),
    (4, 5),
    (5, 4),
    (5, 5)
)

plugin_factory(BaseImagePlugin, 'image', sizes)
