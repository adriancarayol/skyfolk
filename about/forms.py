from ckeditor.widgets import CKEditorWidget
from django import forms

from about.models import PublicationBlog


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = PublicationBlog
        fields = '__all__'
