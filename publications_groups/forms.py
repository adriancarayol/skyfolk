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

    def __init__(self, *args, **kwargs):
        super(GroupPublicationEdit, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationGroup
        fields = ['content', ]
        widgets = {
            'content': forms.Textarea(
                attrs={'required': True, 'placeholder': 'Editar comentario',
                       'class': 'materialize-textarea'
                       }
            )
        }
