from django import forms


class CreateNewYoutubeWidgetForm(forms.Form):
    account_to_search = forms.CharField(required=False, label='Obtener los vídeos subidos por el usuario')
