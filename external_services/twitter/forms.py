from django import forms


class CreateNewTwitterWidgetForm(forms.Form):
    words_to_search = forms.CharField(required=False, max_length=64)
    account_to_search = forms.CharField(required=False)
    only_in_my_account = forms.BooleanField(required=False, initial=False)
