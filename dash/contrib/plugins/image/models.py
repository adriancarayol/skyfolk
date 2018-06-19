import uuid
from django.db import models
from django.contrib.auth.models import User

def upload_dash_image(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return "{0}/{1}".format('dash/images', filename)


class DashImageModel(models.Model):
	image = models.ImageField(upload_to=upload_dash_image)
	user = models.ForeignKey(User)