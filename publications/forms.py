from django import forms

from publications.models import Publication


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        # Excluir atributos en el formulario.
        exclude = ['image', 'created', 'likes', 'user_give_me_like', 'hates',
                    'user_give_me_hate', 'user_share_me']

    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
                'placeholder': 'Escribe tu mensaje aqui...',
                'id': 'message2'
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
                    'user_give_me_hate', 'user_share_me']

    def __init__(self, *args, **kwargs):
        super(ReplyPublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
                'placeholder': 'Escribe tu mensaje aqui...',
                'id': 'message-reply'
            })
        self.fields['content'].label = ''
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['board_owner'].widget = forms.HiddenInput()
        self.fields['parent'].widget = forms.HiddenInput()
