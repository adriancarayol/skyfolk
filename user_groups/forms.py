# encoding:utf-8
from django import forms
from django.contrib.auth.models import User
from .models import UserGroups


class FormUserGroup(forms.ModelForm):
    # users_in_group = forms.ModelMultipleChoiceField(queryset=User.objects.all())

    class Meta:
        model = UserGroups
        fields = ['name', 'description',
                'avatar', 'back_image',
                'is_public']

    def __init__(self, *args, **kwargs):
        super(FormUserGroup, self).__init__(*args, **kwargs)
