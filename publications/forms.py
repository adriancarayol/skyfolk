from django.forms import ModelForm

from publications.models import Publication


class PublicationForm(ModelForm):
    class Meta:
        model = Publication
        exclude = ['image', 'is_response_from', 'created',
                   'author', 'profile', 'likes', 'user_give_me_like', 'hates',
                   'user_give_me_hate']  # Excluir atributos en el formulario.

    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs\
            .update({
                'placeholder': 'Escribe tu mensaje aqui...',
                'id': 'message2'
            })
        self.fields['content'].label = ''
