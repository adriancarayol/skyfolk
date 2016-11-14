# encoding:utf-8
from django import forms
from .models import UserGroups
from django.contrib.auth.models import User

class FormUserGroup(forms.ModelForm):

    class Meta:
        model = UserGroups
        fields = ['name', 'description',
                  'type', 'users', 'small_image',
                  'large_image', 'tags', 'owner', 'privacity', 'users_in_group']

    users_in_group = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.SelectMultiple)

    def __init__(self, *args, **kwargs):
        super(FormUserGroup, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({
                'id': 'description-area',
                'class': 'materialize-textarea',
            })
        self.fields['owner'].widget = forms.HiddenInput()


    def clean_privacity(self):
        privacity = self.cleaned_data['privacity']
        return privacity

