from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField(label='Tu e-mail', max_length=50, required=True)

