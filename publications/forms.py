from django import forms

from publications.models import Publication, PublicationPhoto


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        # Excluir atributos en el formulario.
        exclude = ['image', 'created', 'likes', 'user_give_me_like', 'hates',
                   'user_give_me_hate', 'user_share_me', 'tags', 'deleted', 'event_type']

    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Escribe tu mensaje aqui...',
            'id': 'message2', 'contenteditable': 'true',
            'class': 'materialize-textarea',
            'required': 'required',
        })
        self.fields['content'].label = ''
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['board_owner'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()


class ReplyPublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        # Excluir atributos en el formulario.
        exclude = ['image', 'created', 'likes', 'user_give_me_like', 'hates',
                   'user_give_me_hate', 'user_share_me', 'tags', 'deleted', 'event_type']

    def __init__(self, *args, **kwargs):
        super(ReplyPublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Escribe tu mensaje aqui...',
            'id': 'message-reply', 'contenteditable': 'true',
            'class': 'materialize-textarea',
            'required': 'required',
        })
        self.fields['content'].label = ''
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['board_owner'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()


class PublicationPhotoForm(forms.ModelForm):
    class Meta:
        model = PublicationPhoto
        exclude = ['image', 'created', 'user_give_me_like',
                   'user_give_me_hate', 'user_share_me', 'tags', 'deleted']

    def __init__(self, *args, **kwargs):
        super(PublicationPhotoForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Escribe tu mensaje aqui...',
            'id': 'message-photo', 'contenteditable': 'true',
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
        self.fields['content'].widget.attrs['class'] = 'materialize-textarea'
        self.fields['content'].widget.attrs['id'] = 'edit_comment_content'

    class Meta:
        model = Publication
        fields = ['content', ]
