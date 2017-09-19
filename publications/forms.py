from bs4 import BeautifulSoup
from django import forms

from publications.models import Publication
from publications.utils import parse_string


class PublicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Publication
        # Excluir atributos en el formulario.
        exclude = ['created', 'likes', 'user_give_me_like', 'hates',
                   'user_give_me_hate', 'shared_publication', 'tags', 'deleted',
                   'event_type', 'liked', 'hated', 'shared', 'extra_content', 'shared_photo_publication']


class PublicationEdit(forms.ModelForm):
    """
    Formulario para editar una publicacion existente
    """

    pk = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(PublicationEdit, self).__init__(*args, **kwargs)
        self.fields['pk'].widget.attrs.update({
            'required': 'required', 'hidden': True
        })

    class Meta:
        model = Publication
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


class SharedPublicationForm(forms.ModelForm):
    """
    Formulario para compartir una publicacion existente
    """
    pk = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super(SharedPublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'materialize-textarea',
            'id': 'shared_comment_content',
            'placeholder': 'Añade un comentario...'
        })
        self.fields['content'].required = False
        self.fields['pk'].widget = forms.HiddenInput()

    class Meta:
        model = Publication
        fields = ['content', ]

    def clean_content(self):
        content = self.cleaned_data.get('content', None)

        if not content:
            return content

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
