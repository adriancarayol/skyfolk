from bs4 import BeautifulSoup
from django import forms

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


class SharedGroupPublicationForm(forms.ModelForm):
    """
    Formulario para compartir una publicacion existente
    """
    pk = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(SharedGroupPublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'materialize-textarea',
            'id': 'shared_comment_content',
            'placeholder': 'Añade un comentario...'
        })
        self.fields['content'].required = False
        self.fields['pk'].required = True
        self.fields['pk'].widget = forms.HiddenInput()

    class Meta:
        model = Publication
        fields = ['content', ]

    def clean_content(self):
        content = self.cleaned_data.get('content', None)

        if not content:
            return content

        is_correct_content = False
        pub_content = parse_string(content)  # Comprobamos que el comentario sea correcto
        soup = BeautifulSoup(pub_content)  # Buscamos si entre los tags hay contenido
        for tag in soup.find_all(recursive=True):
            if tag.text and not tag.text.isspace():
                is_correct_content = True
                break

        if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion
            raise forms.ValidationError('El comentario esta vacio')

        if pub_content.isspace():  # Comprobamos si el comentario esta vacio
            raise forms.ValidationError('El comentario esta vacio')

        return content
