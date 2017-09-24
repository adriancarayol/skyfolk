import uuid
import zipfile

try:
    from zipfile import BadZipFile
except ImportError:
    # Python 2.
    from zipfile import BadZipfile as BadZipFile
import logging
import os
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

logger = logging.getLogger('photologue.forms')


class UploadZipForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UploadZipForm, self).__init__(*args, **kwargs)

    zip_file = forms.FileField(help_text=_('Selecciona un zip'))

    title_collection = forms.CharField(
        max_length=250,
        required=False,
        help_text=_('Añade un titulo a las imágenes'))

    caption_collection = forms.CharField(
        required=False,
        help_text=_('Añade una descripcion a las imágenes'))
    is_public_collection = forms.BooleanField(
        initial=False,
        required=False,
        help_text=_('Activa esta casilla para marcar todas las imágenes como privadas'))

    tags_collection = TagField(help_text=_('Añade etiquetas a tu imágen'), required=False)

    def clean_zip_file(self):
        """Open the zip file a first time, to check that it is a valid zip archive.
        We'll open it again in a moment, so we have some duplication, but let's focus
        on keeping the code easier to read!
        """
        zip_file = self.cleaned_data['zip_file']
        try:
            zip = zipfile.ZipFile(zip_file)
        except BadZipFile as e:
            raise forms.ValidationError(str(e))
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            raise forms.ValidationError('"%s" in the .zip archive is corrupt.' % bad_file)
        zip.close()  # Close file in all cases.
        return zip_file

    def clean_title(self):
        title = self.cleaned_data['title_collection']
        if not title:
            raise forms.ValidationError(_('Title is empty.'))
        return title

    def clean(self):
        cleaned_data = super(UploadZipForm, self).clean()
        if not self['title_collection'].errors:
            # If there's already an error in the title, no need to add another
            # error related to the same field.
            if not cleaned_data.get('title_collection', None):
                raise forms.ValidationError(
                    _('Enter a title for a new collection.'))
        return cleaned_data

    def save(self, request=None, zip_file=None):
        if not zip_file:
            zip_file = self.cleaned_data['zip_file']
        zip = zipfile.ZipFile(zip_file)
        count = 1
        current_site = Site.objects.get(id=settings.SITE_ID)

        for filename in sorted(zip.namelist()):

            logger.debug('Reading file "{0}".'.format(filename))

            if filename.startswith('__') or filename.startswith('.'):
                logger.debug('Ignoring file "{0}".'.format(filename))
                continue

            if os.path.dirname(filename):
                logger.warning('Ignoring file "{0}" as it is in a subfolder; all images should be in the top '
                               'folder of the zip.'.format(filename))
                if request:
                    messages.warning(request,
                                     _('Ignoring file "{filename}" as it is in a subfolder; all images should '
                                       'be in the top folder of the zip.').format(filename=filename),
                                     fail_silently=True)
                continue

            data = zip.read(filename)

            if not len(data):
                logger.debug('File "{0}" is empty.'.format(filename))
                continue

            photo_title_root = self.cleaned_data['title_collection'] if self.cleaned_data['title_collection'] else None

            tags = self.cleaned_data['tags_collection']
            photo = Photo.objects.create(title=photo_title_root,
                          caption=self.cleaned_data['caption_collection'],
                          is_public=not self.cleaned_data['is_public_collection'],
                          owner=self.request.user)
            # first add title tag.
            photo.tags.add(self.cleaned_data['title_collection'])
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
                logger.error('Could not process file "{0}" in the .zip archive.'.format(
                    filename))
                if request:
                    messages.warning(request,
                                     _('Could not process file "{0}" in the .zip archive.').format(
                                         filename),
                                     fail_silently=True)
                continue

            contentfile = ContentFile(data)
            photo.image.save(filename, contentfile)
            photo.save()
            photo.sites.add(current_site)
            count += 1

        zip.close()

        if request:
            messages.success(request,
                             _('The photos have been added to publications_gallery "{0}".').format(
                                 self.request.user),
                             fail_silently=True)


class UploadFormPhoto(forms.ModelForm):
    """
    Permite al usuario subir una nueva imagen
    """

    def __init__(self, *args, **kwargs):
        super(UploadFormPhoto, self).__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['image'].widget.attrs.update({'class': 'avatar-input', 'name': 'avatar_file'})
        self.fields['caption'].widget.attrs['class'] = 'materialize-textarea'
        self.fields['is_public'].initial = False

    class Meta:
        model = Photo
        exclude = ('owner', 'date_added', 'sites', 'date_taken', 'slug',)
        help_texts = {
            'url_image': 'Introduce una URL con una imagen',
            'title': 'Añade un titulo a la imágen',
            'caption': 'Añade una descripcion a la imágen',
            'tags': 'Añade etiquetas a tu imágen',
            'is_public': 'Activa esta casilla para marcar la imágen como privada',
        }


class EditFormPhoto(forms.ModelForm):
    """
    Permite al usuario editar una foto ya existente
    """

    def __init__(self, *args, **kwargs):
        super(EditFormPhoto, self).__init__(*args, **kwargs)
        self.fields['caption'].widget.attrs['class'] = 'materialize-textarea'

    class Meta:
        model = Photo
        exclude = ('owner', 'date_added', 'sites',
                   'date_taken', 'slug', 'is_public', 'image',
                   'crop_from')


class UploadFormVideo(forms.ModelForm):
    """
    Permite al usuario subir un nuevo video
    """

    def __init__(self, *args, **kwargs):
        super(UploadFormVideo, self).__init__(*args, **kwargs)
        self.fields['video'].required = False
        self.fields['video'].widget.attrs.update({'class': 'avatar-input', 'name': 'avatar_file'})
        self.fields['caption'].widget.attrs['class'] = 'materialize-textarea'
        self.fields['is_public'].initial = False

    class Meta:
        model = Video
        fields = ('name', 'caption', 'is_public', 'tags', 'video')
        help_texts = {
            'name': 'Añade un título al vídeo',
            'caption': 'Añade una descripcion al vídeo',
            'tags': 'Añade etiquetas a tu vídeo',
            'is_public': 'Activa esta casilla para marcar el vídeo como privada',
        }