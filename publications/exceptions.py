from django.forms import ValidationError


class EmptyContent(ValidationError):
    """
    Contenido de la publicacion vacio
    """

    pass


class MediaNotSupported(ValidationError):
    """
    Formato de los adjuntos no valido
    """

    pass


class SizeIncorrect(ValidationError):
    """
    El tamaño del archivo es incorrecto
    """

    pass


class MaxFilesReached(ValidationError):
    """
    El numero de archivos ha sido superado
    """

    pass


class CantOpenMedia(ValidationError):
    """
    No se pudo leer uno de los archivos
    """

    pass
