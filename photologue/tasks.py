from skyfolk.celery import app
from easy_thumbnails.files import generate_all_aliases


@app.task(name='generate_thumbnail')
def generate_thumbnails(model, pk, field):
    instance = model._default_manager.get(pk=pk)
    thumbnail = getattr(instance, field)
    generate_all_aliases(thumbnail, include_global=True)
