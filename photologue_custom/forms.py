from django import forms
from .models import PhotoExtended
from photologue.models import Photo

class UploadNewPhotoExtended(forms.ModelForm):

    class Meta:
        model = PhotoExtended
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UploadNewPhotoExtended, self).__init__(*args, **kwargs)

        self.fields['owner'].widget = forms.HiddenInput()
        self.fields['photo'].widget = forms.HiddenInput()

class UploadNewPhoto(forms.ModelForm):

    class Meta:
        model = Photo
        exclude = ('sites', )

    def __init__(self, *args, **kwargs):
        super(UploadNewPhoto, self).__init__(*args, **kwargs)