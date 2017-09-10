from bs4 import BeautifulSoup
from django import forms

from emoji import Emoji
from publications.models import Publication
from publications.utils import parse_string
from publications_groups.models import PublicationGroup


class PublicationGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationGroupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationGroup
        # Excluir atributos en el formulario.
        fields = ['content', 'parent']


class ReplyPublicationGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReplyPublicationGroupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationGroup
        # Excluir atributos en el formulario.
        fields = ['content', 'parent']


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

