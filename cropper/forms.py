from django import forms

class FileUploadForm(forms.Form):
    docfile = forms.FileField()
    
    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['docfile'].widget.attrs.update({'class': 'avatar-input', 'id': 'avatarInput', 'name': 'avatar_file'})