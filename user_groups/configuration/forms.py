from django import forms

from user_groups.forms import CommaSeparatedCharField
from user_groups.models import UserGroups


class ConfigurationGroupForm(forms.ModelForm):
    tags = CommaSeparatedCharField(
        max_length=240,
        initial="222",
        required=False,
        widget=forms.TextInput(attrs={"id": "edit_tags"}),
    )

    def __init__(self, *args, **kwargs):
        super(ConfigurationGroupForm, self).__init__(auto_id=False, *args, **kwargs)

    class Meta:
        model = UserGroups
        fields = ["description", "avatar", "back_image", "is_public"]
        widgets = {
            "description": forms.TextInput(attrs={"id": "edit_description"}),
            "avatar": forms.FileInput(attrs={"id": "edit_avatar"}),
            "back_image": forms.FileInput(attrs={"id": "edit_back_image"}),
            "is_public": forms.CheckboxInput(attrs={"id": "edit_is_public"}),
        }

    def clean_is_public(self):
        is_public = self.cleaned_data["is_public"]
        return not is_public

    def clean_tags(self):
        tags = self.cleaned_data["tags"]
        if len(tags) > 240:
            raise forms.ValidationError(
                "Prueba a introducir menos de 240 caracteres en el campo de intereses."
            )
        return set(tags)
