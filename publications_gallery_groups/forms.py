import logging
from django import forms

from publications_gallery_groups.models import PublicationGroupMediaVideo, PublicationGroupMediaPhoto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublicationPhotoForm(forms.ModelForm):
    class Meta:
        model = PublicationGroupMediaPhoto
        exclude = ['image', 'created', 'user_give_me_like', 'author',
                   'user_give_me_hate', 'tags', 'deleted', 'event_type', 'edition_date']

    def __init__(self, *args, **kwargs):
        super(PublicationPhotoForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Escribe tu mensaje aqui...',
            'id': 'message-photo',
            'class': 'materialize-textarea',
            'required': 'required',
        })
        self.fields['content'].label = ''
        self.fields['board_photo'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()

    def clean_content(self):
        content = self.cleaned_data['content']

        if content.isspace():  # Comprobamos si el comentario esta vacio
            raise forms.ValidationError('¡Comprueba el texto del comentario!')

        return content


class PublicationPhotoEdit(forms.ModelForm):
    """
    Formulario para editar una publicacion existente
    """

    pk = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(PublicationPhotoEdit, self).__init__(*args, **kwargs)
        self.fields['pk'].widget.attrs.update({
            'required': 'required', 'hidden': True
        })

    class Meta:
        model = PublicationGroupMediaPhoto
        fields = ['content', ]

    def clean_content(self):
        content = self.cleaned_data.get('content', None)

        if not content:
            raise forms.ValidationError('El comentario esta vacio')

        if content.isspace():  # Comprobamos si el comentario esta vacio
            raise forms.ValidationError('El comentario esta vacio')

        return content

    def clean_pk(self):
        pk = self.cleaned_data.get('pk', None)
        if not pk:
            raise forms.ValidationError('No existe la publicación solicitada.')
        return pk


# Video form

class PublicationVideoForm(forms.ModelForm):
    class Meta:
        model = PublicationGroupMediaVideo
        exclude = ['image', 'created', 'user_give_me_like', 'author',
                   'user_give_me_hate', 'tags', 'deleted', 'event_type', 'edition_date']

    def __init__(self, *args, **kwargs):
        super(PublicationVideoForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Escribe tu mensaje aqui...',
            'id': 'message-photo',
            'class': 'materialize-textarea',
            'required': 'required',
        })
        self.fields['content'].label = ''
        self.fields['board_video'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()

    def clean_content(self):
        content = self.cleaned_data['content']

        if content.isspace():  # Comprobamos si el comentario esta vacio
            raise forms.ValidationError('¡Comprueba el texto del comentario!')

        return content


class PublicationVideoEdit(forms.ModelForm):
    """
    Formulario para editar una publicacion existente
    """

    pk = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(PublicationVideoEdit, self).__init__(*args, **kwargs)
        self.fields['pk'].widget.attrs.update({
            'required': 'required', 'hidden': True
        })

    class Meta:
        model = PublicationGroupMediaVideo
        fields = ['content', ]

    def clean_content(self):
        content = self.cleaned_data.get('content', None)

        if not content:
            raise forms.ValidationError('El comentario esta vacio')

        if content.isspace():  # Comprobamos si el comentario esta vacio
            raise forms.ValidationError('El comentario esta vacio')

        return content

    def clean_pk(self):
        pk = self.cleaned_data.get('pk', None)
        if not pk:
            raise forms.ValidationError('No existe la publicación solicitada.')
        return pk
