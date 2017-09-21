import logging
from bs4 import BeautifulSoup
from django import forms

from emoji import Emoji
from publications_groups.models import PublicationGroup
from publications_groups.themes.models import PublicationTheme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublicationGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationGroupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationGroup
        # Excluir atributos en el formulario.
        fields = ['content', 'parent']

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


class GroupPublicationEdit(forms.ModelForm):
    """
    Formulario para editar una publicacion existente
    """
    pk = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(GroupPublicationEdit, self).__init__(*args, **kwargs)
        self.fields['pk'].widget.attrs.update({
            'required': 'required', 'hidden': True
        })

    class Meta:
        model = PublicationGroup
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


class PublicationThemeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationThemeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationTheme
        # Excluir atributos en el formulario.
        fields = ['content', 'parent', 'board_theme']

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

        return Emoji.replace(content)