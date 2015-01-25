from django import template
from datetime import date, timedelta
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

register = template.Library()


@register.filter(name='file_exists')
def file_exists(value):
    return default_storage.exists(value)


@register.filter(name='url_exists')
def url_exists(value):
    # NO LO HE PROBADO TODAVIA, PUEDE QUE NO FUNCIONE
    validate = URLValidator(verify_exists=True)
    try:
        validate('http://www.somelink.com/to/my.pdf')
        return True
    except ValidationError:
        return False
