import json
import os
from django.utils.six import BytesIO
from django.shortcuts import render
from .forms import FileUploadForm
from .models import Document
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse

def cropper_js(request):
    if request.method == 'POST':
        form = FileUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            img_data = dict(request.POST.items())

            x = None # Coordinate x
            y = None # Coordinate y
            w = None # Width
            h = None # Height
            rotate = None # Rotate
            for key, value in img_data.items():
                if key == "avatar_data":
                    str_value = json.loads(value)
                    print(str_value)
                    x = str_value.get('x')
                    y = str_value.get('y')
                    w = str_value.get('width')
                    h = str_value.get('height')
                    rotate = str_value.get('rotate')

            print('x: {}, y: {}, w: {}, h: {}, rotate: {}'.format(x, y, w, h, rotate))

            im = Image.open(request.FILES['docfile']).convert('RGBA')

            tempfile = im.rotate(-rotate, expand=True)
            tempfile = tempfile.crop((int(x), int(y), int(w+x), int(h+y)))
            tempfile_io = BytesIO()
            tempfile_io.seek(0, os.SEEK_END)
            tempfile.save(tempfile_io, format='PNG')
            image_file = InMemoryUploadedFile(tempfile_io, None, 'rotate.png', 'image/png', tempfile_io.tell(), None)

            newdoc = Document()
            newdoc.docfile.save('rotate.png', image_file)
            newdoc.save()
            data = {
                'result': True,
                'state': 200,
                'message': 'Success',
            }
            return JsonResponse({'data': data})
        else:
            print('Uncut image!')
            print(form.errors)
    documents = Document.objects.all()
    context = {'form': FileUploadForm, 'documents': documents}
    return render(request, "index.html", context)