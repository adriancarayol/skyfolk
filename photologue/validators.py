import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.gif', '.png', '.jpeg', '.jpg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_extension(ext):
    valid_extensions = ['.gif', '.png', '.jpeg', '.jpg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_video(value):
    ''' if value.file is an instance of InMemoryUploadedFile, it means that the
    file was just uploaded with this request (i.e., it's a creation process,
    not an editing process. '''
    if isinstance(value.video, InMemoryUploadedFile) and value.file.content_type.split('/').lower()[
        1] not in settings.VIDEO_EXTENTIONS:
        raise ValidationError('Please upload a valid video file')
