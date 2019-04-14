from django import template
from django.contrib.humanize.templatetags.humanize import intword

register = template.Library()


@register.filter(name="zero_to_empty")
def zero_to_empty(value):
    if not value or value <= 0:
        return ""
    return intword(value)
