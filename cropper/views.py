from django.shortcuts import render
from .forms import FileUploadForm
from .models import Document
from PIL import Image
from io import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import json


def cropper_js(request):
    if request.method == 'POST':
        form = FileUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            img_data = dict(request.POST.iteritems())

            x = None
            y = None
            w = None
            h = None
            rotate = None
            for key, value in img_data.iteritems():
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
            tempfile_io = StringIO.StringIO()
            tempfile.save(tempfile_io, format='PNG')
            image_file = InMemoryUploadedFile(tempfile_io, None, 'rotate.png', 'image/png', tempfile_io.len, None)

            newdoc = Document()
            newdoc.docfile.save('rotate.png', image_file)
            newdoc.save()
            
            print('valid form')
        else:
            print('invalid form')
            print(form.errors)
    documents = Document.objects.all()
    context = {'form': FileUploadForm, 'documents': documents}
    return render(request, "index.html", context)