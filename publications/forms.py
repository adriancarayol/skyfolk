#encoding:utf-8
from django.forms import ModelForm
from publications.models import Publication

class PublicationForm(ModelForm):
    class Meta:
        model = Publication
        exclude = ('image', 'is_response_from', 'created',)