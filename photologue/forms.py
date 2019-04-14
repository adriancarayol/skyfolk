import tempfile
import zipfile
from photologue.validators import valid_url_extension, valid_url_mimetype
from publications.utils import convert_video_to_mp4

try:
    from zipfile import BadZipFile
except ImportError:
    # Python 2.
    from zipfile import BadZipfile as BadZipFile
import logging
import os
import magic
from io import BytesIO

try:
    import Image
except ImportError:
    from PIL import Image

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.files.base import ContentFile
from taggit.forms import TagField
from .models import Photo, Video
from .utils.utils import split_url, generate_path_video

logger = logging.getLogger("photologue.forms")


class UploadZipForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UploadZipForm, self).__init__(*args, **kwargs)

    zip_file = forms.FileField(help_text=_("Selecciona un zip"))

    title_collection = forms.CharField(
        max_length=250, required=False, help_text=_("Añade un titulo a las imágenes")
    )

    caption_collection = forms.CharField(
        required=False, help_text=_("Añade una descripcion a las imágenes")
    )
    is_public_collection = forms.BooleanField(
        initial=False,
        required=False,
        help_text=_("Activa esta casilla para marcar todas las imágenes como privadas"),
    )

    tags_collection = TagField(
        help_text=_("Añade etiquetas a tu imágen"), required=False
    )

    def clean_zip_file(self):
        """Open the zip file a first time, to check that it is a valid zip archive.
        We'll open it again in a moment, so we have some duplication, but let's focus
        on keeping the code easier to read!
        """
        zip_file = self.cleaned_data["zip_file"]
        try:
            zip = zipfile.ZipFile(zip_file)
        except BadZipFile as e:
            raise forms.ValidationError(str(e))
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            raise forms.ValidationError(
                '"%s" in the .zip archive is corrupt.' % bad_file
            )
        zip.close()  # Close file in all cases.
        return zip_file

    def clean_title(self):
        title = self.cleaned_data["title_collection"]
        if not title:
            raise forms.ValidationError(_("Title is empty."))
        return title

    def clean(self):
        cleaned_data = super(UploadZipForm, self).clean()
        if not self["title_collection"].errors:
            # If there's already an error in the title, no need to add another
            # error related to the same field.
            if not cleaned_data.get("title_collection", None):
                raise forms.ValidationError(_("Enter a title for a new collection."))
        return cleaned_data

    def save(self, request=None, zip_file=None):
        if not zip_file:
            zip_file = self.cleaned_data["zip_file"]
        zip = zipfile.ZipFile(zip_file)
        count = 1
        current_site = Site.objects.get(id=settings.SITE_ID)

        for filename in sorted(zip.namelist()):

            logger.debug('Reading file "{0}".'.format(filename))

            if filename.startswith("__") or filename.startswith("."):
                logger.debug('Ignoring file "{0}".'.format(filename))
                continue

            if os.path.dirname(filename):
                logger.warning(
                    'Ignoring file "{0}" as it is in a subfolder; all images should be in the top '
                    "folder of the zip.".format(filename)
                )
                if request:
                    messages.warning(
                        request,
                        _(
                            'Ignoring file "{filename}" as it is in a subfolder; all images should '
                            "be in the top folder of the zip."
                        ).format(filename=filename),
                        fail_silently=True,
                    )
                continue

            data = zip.read(filename)

            if not len(data):
                logger.debug('File "{0}" is empty.'.format(filename))
                continue

            photo_title_root = (
                self.cleaned_data["title_collection"]
                if self.cleaned_data["title_collection"]
                else None
            )

            tags = self.cleaned_data["tags_collection"]
            photo = Photo.objects.create(
                title=photo_title_root,
                caption=self.cleaned_data["caption_collection"],
                is_public=not self.cleaned_data["is_public_collection"],
                owner=self.request.user,
            )
            # first add title tag.
            photo.tags.add(self.cleaned_data["title_collection"])
            for tag in tags:
                photo.tags.add(tag)
            # Basic check that we have a valid image.
            try:
                file = BytesIO(data)
                opened = Image.open(file)
                opened.verify()
            except Exception:
                # Pillow (or PIL) doesn't recognize it as an image.
                # If a "bad" file is found we just skip it.
                # But we do flag this both in the logs and to the user.
                logger.error(
                    'Could not process file "{0}" in the .zip archive.'.format(filename)
                )
                if request:
                    messages.warning(
                        request,
                        _('Could not process file "{0}" in the .zip archive.').format(
                            filename
                        ),
                        fail_silently=True,
                    )
                continue

            contentfile = ContentFile(data)
            photo.image.save(filename, contentfile)
            photo.save()
            photo.sites.add(current_site)
            count += 1

        zip.close()

        if request:
            messages.success(
                request,
                _('The photos have been added to publications_gallery "{0}".').format(
                    self.request.user
                ),
                fail_silently=True,
            )


class UploadFormPhoto(forms.ModelForm):
    """
    Permite al usuario subir una nueva imagen
    """

    def __init__(self, *args, **kwargs):
        super(UploadFormPhoto, self).__init__(*args, **kwargs)
        self.fields["image"].required = False
        self.fields["image"].widget.attrs.update(
            {"class": "avatar-input", "name": "avatar_file"}
        )
        self.fields["caption"].widget.attrs["class"] = "materialize-textarea"
        self.fields["is_public"].initial = False

    def clean(self):
        cleaned_data = super(UploadFormPhoto, self).clean()
        image = self.cleaned_data.get("image", None)
        url = self.cleaned_data.get("url_image", None)

        if not image and not url:
            raise forms.ValidationError("image", "Debes escoger una imágen o una URL.")

        return cleaned_data

    def clean_url_image(self):
        url_image = self.cleaned_data["url_image"]

        if url_image:
            domain, path = split_url(url_image)
            if not valid_url_extension(url_image) or not valid_url_mimetype(url_image):
                raise forms.ValidationError(
                    _("No es una imágen válida. Sólo se aceptan: (.jpg/.jpeg/.png)")
                )

        return url_image

    class Meta:
        model = Photo
        exclude = ("owner", "date_added", "sites", "date_taken", "slug")
        help_texts = {
            "url_image": "Introduce una URL con una imagen",
            "title": "Añade un titulo a la imágen",
            "caption": "Añade una descripcion a la imágen",
            "tags": "Añade etiquetas a tu imágen",
            "is_public": "Activa esta casilla para marcar la imágen como privada",
        }


class EditFormPhoto(forms.ModelForm):
    """
    Permite al usuario editar una foto ya existente
    """

    def __init__(self, *args, **kwargs):
        super(EditFormPhoto, self).__init__(*args, **kwargs)
        self.fields["caption"].widget.attrs["class"] = "materialize-textarea"

    class Meta:
        model = Photo
        exclude = (
            "owner",
            "date_added",
            "sites",
            "date_taken",
            "slug",
            "is_public",
            "image",
            "crop_from",
        )


class UploadFormVideo(forms.ModelForm):
    """
    Permite al usuario subir un nuevo video
    """

    def __init__(self, *args, **kwargs):
        super(UploadFormVideo, self).__init__(*args, **kwargs)
        self.fields["video"].required = False
        self.fields["video"].widget.attrs.update(
            {"class": "avatar-input", "name": "avatar_file"}
        )
        self.fields["caption"].widget.attrs.update(
            {"class": "materialize-textarea", "id": "id_caption_video"}
        )
        self.fields["is_public"].initial = False
        self.fields["is_public"].widget.attrs.update({"id": "id_is_public_video"})
        self.fields["tags"].widget.attrs.update({"id": "id_tags_video"})
        self.fields["name"].widget.attrs.update({"id": "id_name_video"})

    def clean_video(self):
        video = self.cleaned_data.get("video", None)

        if not video:
            raise forms.ValidationError("Debes seleccionar un vídeo.")

        if video.size > settings.BACK_IMAGE_DEFAULT_SIZE:
            raise forms.ValidationError("El video seleccionado ocupa más de 5MB.")

        type = magic.from_buffer(video.read(1024), mime=True)

        if type.split("/")[0] != "video":
            raise forms.ValidationError("Selecciona un formato de vídeo válido.")

        if type != "video/mp4":
            tmp = tempfile.NamedTemporaryFile(delete=False)

            for block in video.chunks():
                tmp.write(block)

            mp4_path = "{0}{1}".format(tmp.name, ".mp4")
            return_code = convert_video_to_mp4(tmp.name, mp4_path)

            if return_code:
                raise forms.ValidationError(
                    "Hubo un error al procesar tu vídeo, intentalo de nuevo."
                )

            return mp4_path

        return video

    class Meta:
        model = Video
        fields = ("name", "caption", "is_public", "tags", "video")
        help_texts = {
            "name": "Añade un título al vídeo",
            "caption": "Añade una descripcion al vídeo",
            "tags": "Añade etiquetas a tu vídeo",
            "is_public": "Activa esta casilla para marcar el vídeo como privado",
            "video": "Selecciona un vídeo",
        }


class EditFormVideo(forms.ModelForm):
    """
    Permite al usuario editar un video ya existente
    """

    def __init__(self, *args, **kwargs):
        super(EditFormVideo, self).__init__(*args, **kwargs)
        self.fields["caption"].widget.attrs["class"] = "materialize-textarea"

    class Meta:
        model = Video
        exclude = ("owner", "date_added", "slug", "is_public", "video")
