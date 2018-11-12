from django import forms


class CreateNewTwitterWidgetForm(forms.Form):
    word_to_search = forms.CharField(required=False, max_length=64)
    account_to_search = forms.CharField(required=False)
