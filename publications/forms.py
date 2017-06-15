from django import forms
from publications.models import Publication, PublicationPhoto, PublicationImage


class PublicationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Publication
        # Excluir atributos en el formulario.
        exclude = ['created', 'likes', 'user_give_me_like', 'hates',
                   'user_give_me_hate', 'shared_publication', 'tags', 'deleted',
                   'event_type', 'liked', 'hated', 'shared', 'extra_content']

        """
        if self.initial:
            if self.initial['author'] == self.initial['board_owner']: # Publico en mi perfil
                self.fields['content'].widget.attrs.update({
                'class': 'materialize-textarea',
                'id': 'message2',
                'data-length': '500',
                'placeholder': 'Escribe tu mensaje aqui...',
                'required': 'required',
                })
            else: # Publico en perfil ajeno
                self.fields['content'].widget.attrs.update({
                'class': 'materialize-textarea',
                'id': 'message3',
                'data-length': '500',
                'placeholder': 'Escribe tu mensaje aqui...',
                'required': 'required',
                })

        self.fields['content'].label = ''
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['board_owner'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()
        """


class ReplyPublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        # Excluir atributos en el formulario.
        exclude = ['image', 'created', 'likes', 'user_give_me_like', 'hates',
                   'user_give_me_hate', 'shared_publication', 'tags', 'deleted', 
                   'event_type', 'liked', 'hated', 'shared', 'extra_content']

    def __init__(self, *args, **kwargs):
        super(ReplyPublicationForm, self).__init__(*args, **kwargs)


class PublicationPhotoForm(forms.ModelForm):
    class Meta:
        model = PublicationPhoto
        exclude = ['image', 'created', 'user_give_me_like',
                   'user_give_me_hate', 'user_share_me', 'tags', 'deleted']

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


class PublicationEdit(forms.ModelForm):
    """
    Formulario para editar una publicacion existente
    """
    def __init__(self, *args, **kwargs):
        super(PublicationEdit, self).__init__(*args, **kwargs)

    class Meta:
        model = Publication
        fields = ['content', ]


class SharedPublicationForm(forms.ModelForm):
    """
    Formulario para compartir una publicacion existente
    """

    def __init__(self, *args, **kwargs):
        super(SharedPublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'materialize-textarea',
            'id': 'shared_comment_content',
            'placeholder': 'Añade un comentario...'
        })
        self.fields['content'].required = False

    class Meta:
        model = Publication
        fields = ['content', ]