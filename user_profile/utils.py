import uuid, os
from django.conf import settings
from user_profile.models import NodeProfile

def handle_uploaded_file(f, file_id):
    filename, file_extension = os.path.splitext(f.name)
    dir_path = settings.MEDIA_ROOT + '/back_images/'

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = dir_path + file_id + file_extension

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
