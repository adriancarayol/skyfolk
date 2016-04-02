from django import template
import re
register = template.Library()

@register.filter(name='replaceTags')
def replaceTags(content):
    content = re.sub(r'<[^>]*>', r'', content)  # eliminamos html tags
    return content