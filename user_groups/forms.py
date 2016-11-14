# encoding:utf-8
from django import forms
from .models import UserGroups

class FormUserGroup(forms.ModelForm):

    class Meta:
        model = UserGroups
        fields = ['name', 'description',
                  'type', 'users', 'small_image',
                  'large_image', 'tags', 'owner']

    def __init__(self, *args, **kwargs):
        super(FormUserGroup, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Escribe una descripcion para tu grupo'
            })
        self.fields['owner'].widget = forms.HiddenInput()
