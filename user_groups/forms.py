# encoding:utf-8
import bleach
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
    tags = CommaSeparatedCharField(max_length=240)

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

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if len(tags) > 240:
            raise forms.ValidationError('Prueba a introducir menos de 240 caracteres en el campo de intereses.')
        return set(tags)


class GroupThemeForm(forms.ModelForm):
    class Meta:
        model = GroupTheme
        fields = ['description', 'title', 'image', 'board_group', ]
        widgets = {
            'board_group': forms.HiddenInput(),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        title = title.replace('\n', '').replace('\r', '')
        title = bleach.clean(title, tags=[''])
        return Emoji.replace(title)

    def clean_description(self):
        description = self.cleaned_data['description']
        description = description.replace('\n', '').replace('\r', '')
        description = bleach.clean(description, tags=[''])
        description = bleach.linkify(description)
        return Emoji.replace(description)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
                raise forms.ValidationError('La imagen no puede ser superior a 5MB')
        return image


class EditGroupThemeForm(forms.ModelForm):
    pk = forms.IntegerField(label='')

    def __init__(self, *args, **kwargs):
        super(EditGroupThemeForm, self).__init__(*args, **kwargs)
        self.fields['pk'].widget.attrs.update({
            'required': 'required', 'hidden': True
        })

    class Meta:
        model = GroupTheme
        fields = ['description', 'title', 'image', 'board_group', ]
        widgets = {
            'board_group': forms.HiddenInput(),
            'image': forms.FileInput()
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        title = title.replace('\n', '').replace('\r', '')
        title = bleach.clean(title, tags=[''])
        return Emoji.replace(title)

    def clean_description(self):
        description = self.cleaned_data['description']
        description = description.replace('\n', '').replace('\r', '')
        description = bleach.clean(description, tags=[''])
        description = bleach.linkify(description)
        return Emoji.replace(description)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
                raise forms.ValidationError('La imagen no puede ser superior a 5MB')
        return image

    def clean_pk(self):
        pk = self.cleaned_data.get('pk', None)
        if not pk:
            raise forms.ValidationError('No existe la publicación solicitada.')
        return pk
