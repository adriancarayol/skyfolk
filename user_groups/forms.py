# encoding:utf-8
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.conf import settings

from emoji import Emoji
from user_groups.models import GroupTheme
from .models import UserGroups


class MinLengthValidator(validators.MinLengthValidator):
    message = 'Ensure this value has at least %(limit_value)d elements (it has %(show_value)d).'


class MaxLengthValidator(validators.MaxLengthValidator):
    message = 'Ensure this value has at most %(limit_value)d elements (it has %(show_value)d).'


class CommaSeparatedCharField(forms.Field):
    def __init__(self, dedup=True, max_length=None, min_length=None, *args, **kwargs):
        self.dedup, self.max_length, self.min_length = dedup, max_length, min_length
        super(CommaSeparatedCharField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return []

        value = [item.strip() for item in value.split(',') if item.strip()]
        if self.dedup:
            value = list(set(value))

        return value

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value


class CommaSeparatedIntegerField(forms.Field):
    default_error_messages = {
        'invalid': 'Enter comma separated numbers only.',
    }

    def __init__(self, dedup=True, max_length=None, min_length=None, *args, **kwargs):
        self.dedup, self.max_length, self.min_length = dedup, max_length, min_length
        super(CommaSeparatedIntegerField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return []

        try:
            value = [int(item.strip()) for item in value.split(',') if item.strip()]
            if self.dedup:
                value = list(set(value))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'])

        return value

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value


class FormUserGroup(forms.ModelForm):
    # users_in_group = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    tags = CommaSeparatedCharField(max_length=120)

    class Meta:
        model = UserGroups
        fields = ['name', 'description',
                  'avatar', 'back_image',
                  'is_public']

    def __init__(self, *args, **kwargs):
        super(FormUserGroup, self).__init__(*args, **kwargs)
        self.fields['is_public'].initial = False
        self.fields['tags'].required = False

    def clean_is_public(self):
        is_public = self.cleaned_data['is_public']
        return not is_public


class GroupThemeForm(forms.ModelForm):
    class Meta:
        model = GroupTheme
        fields = ['description', 'title', 'image', 'board_group', ]
        widgets = {
            'board_group': forms.HiddenInput(),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        return Emoji.replace(title)

    def clean_description(self):
        description = self.cleaned_data['description']
        return Emoji.replace(description)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
                raise forms.ValidationError('La imagen no puede ser superior a 5MB')
        return image