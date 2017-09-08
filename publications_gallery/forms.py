from django import forms

from publications.models import Publication
from publications_gallery.models import PublicationPhoto


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


class SharedPhotoPublicationForm(forms.ModelForm):
    """
    Formulario para compartir una publicacion existente
    """

    def __init__(self, *args, **kwargs):
        super(SharedPhotoPublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'materialize-textarea',
            'id': 'shared_comment_content',
            'placeholder': 'Añade un comentario...'
        })
        self.fields['content'].required = False

    class Meta:
        model = Publication
        fields = ['content', ]