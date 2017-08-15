from django import forms

from publications_groups.models import PublicationGroup


class PublicationGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationGroupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationGroup
        # Excluir atributos en el formulario.
        fields = ['content', ]


class ReplyPublicationGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReplyPublicationGroupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PublicationGroup
        # Excluir atributos en el formulario.
        fields = ['content', ]
