# encoding:utf-8
from django import forms

from .models import UserGroups


class FormUserGroup(forms.ModelForm):
    # users_in_group = forms.ModelMultipleChoiceField(queryset=User.objects.all())

    class Meta:
        model = UserGroups
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(FormUserGroup, self).__init__(*args, **kwargs)