import uuid
from dash.mixins import DashboardEntryMixin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.six import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from ....base import DashboardPluginFormBase
from .models import DashImageModel


__title__ = "dash.contrib.plugins.image.forms"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = ("ImageForm",)


class ImageForm(DashboardEntryMixin, DashboardPluginFormBase):
    """Image form for `ImagePlugin` plugin."""

    plugin_data_fields = [("title", ""), ("image", "")]

    title = forms.CharField(label=_("Title"), required=True)
    image = forms.ImageField(label=_("Image"), required=True)

    def save_plugin_data(self, request=None):
        """Saving the plugin data and moving the file."""
        maxsize = (600, 350)
        image = self.cleaned_data.get("image", None)

        img = Image.open(image)
        img = img.convert("RGBA")

        fill_color = (255, 255, 255, 0)
        if img.mode in ("RGBA", "LA"):
            background = Image.new(img.mode[:-1], img.size, fill_color)
            background.paste(img, img.split()[-1])
            img = background

        img.thumbnail(maxsize)
        tempfile_io = BytesIO()
        img.save(tempfile_io, "JPEG")
        tempfile_io.seek(0)

        image_file = InMemoryUploadedFile(
            tempfile_io,
            None,
            str(uuid.uuid4()) + "rotate.jpeg",
            "image/jpeg",
            tempfile_io.tell(),
            None,
        )

        if image_file:
            im = DashImageModel.objects.create(
                image=image_file, user_id=request.user.id
            )
            self.cleaned_data["image"] = im.id
