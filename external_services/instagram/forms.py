from django import forms


class CreateNewInstagramWidgetForm(forms.Form):
    word_to_search = forms.CharField(required=False, max_length=64)
    account_to_search = forms.CharField(required=False)
