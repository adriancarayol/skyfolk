import logging
from bs4 import BeautifulSoup
from django import forms

from publications_gallery.models import PublicationPhoto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublicationPhotoForm(forms.ModelForm):
    class Meta:
        model = PublicationPhoto
        exclude = ['image', 'created', 'user_give_me_like',
                   'user_give_me_hate', 'user_share_me', 'tags', 'deleted', 'event_type']

    def __init__(self, *args, **kwargs):
        super(PublicationPhotoForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Escribe tu mensaje aqui...',
            'id': 'message-photo',
            'class': 'materialize-textarea',
            'required': 'required',
        })
        self.fields['content'].label = ''
        self.fields['p_author'].widget = forms.HiddenInput()
        self.fields['board_photo'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()

    def clean_content(self):
        content = self.cleaned_data['content']

        is_correct_content = False

        soup = BeautifulSoup(content)  # Buscamos si entre los tags hay contenido
        for tag in soup.find_all(recursive=True):
            if tag.text and not tag.text.isspace():
                is_correct_content = True
                break

        if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion

            logger.info('Publicacion contiene espacios o no tiene texto')
            raise forms.ValidationError('¡Comprueba el texto del comentario!')

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
        model = PublicationPhoto
        fields = ['content', ]

    def clean_content(self):
        content = self.cleaned_data.get('content', None)

        if not content:
            raise forms.ValidationError('El comentario esta vacio')

        is_correct_content = False
        soup = BeautifulSoup(content)  # Buscamos si entre los tags hay contenido
        for tag in soup.find_all(recursive=True):
            if tag.text and not tag.text.isspace():
                is_correct_content = True
                break

        if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion
            raise forms.ValidationError('El comentario esta vacio')

        if content.isspace():  # Comprobamos si el comentario esta vacio
            raise forms.ValidationError('El comentario esta vacio')

        return content

    def clean_pk(self):
        pk = self.cleaned_data.get('pk', None)
        if not pk:
            raise forms.ValidationError('No existe la publicación solicitada.')
        return pk
