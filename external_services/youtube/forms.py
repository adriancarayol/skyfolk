from django import forms


class CreateNewYoutubeWidgetForm(forms.Form):
    word_to_search = forms.CharField(required=False, max_length=64, label='Palabra o frase a buscar')
    account_to_search = forms.CharField(required=False, label='Obtener los últimos tweets de @nombre_de_usuario')
