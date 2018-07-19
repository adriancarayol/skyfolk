from django.utils.translation import ugettext_lazy as _

from ....base import BaseDashboardPlugin
from ....factory import plugin_factory
from .models import DashImageModel
from .forms import ImageForm
from .helpers import delete_file, clone_file

__title__ = 'dash.contrib.plugins.image.dash_plugins'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2013-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('BaseImagePlugin',)


# ****************************************************************************
# ***************************** Base Image plugin ****************************
# ****************************************************************************


class BaseImagePlugin(BaseDashboardPlugin):
    """Base image plugin."""

    name = _("Image")
    group = _("Image")
    form = ImageForm
    html_classes = ['pictonic']

    def delete_plugin_data(self):
        """Deletes uploaded file."""
        im = DashImageModel.objects.get(id=self.data.image)
        im.image.delete()
        im.delete()

    def clone_plugin_data(self, dashboard_entry):
        """Clone plugin data, which means we make a copy of the original image.

        TODO: Perhaps rely more on data of ``dashboard_entry``?
        """
        im = DashImageModel.objects.get(id=self.data.image)
        cloned_image = clone_file(im.image, relative_path=False)
        return self.get_cloned_plugin_data(update={'image': cloned_image})


# ****************************************************************************
# ********** Generating and registering the plugins using factory ************
# ****************************************************************************


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
