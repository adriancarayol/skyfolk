from django import template

from ..models import Photo

register = template.Library()


@register.tag
def get_photo(parser, token):
    """Get a single photo from the photologue library and return the img tag to display it.

    Takes 3 args:
    - the photo to display. This can be either the slug of a photo, or a variable that holds either a photo instance or
      a integer (photo id)
    - the photosize to use.
    - a CSS class to apply to the img tag.
    """
    try:
        # Split the contents of the tag, i.e. tag name + argument.
        tag_name, photo, photosize, css_class = token.split_contents()
    except ValueError:
        msg = "%r tag requires 3 arguments" % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    return PhotoNode(photo, photosize[1:-1], css_class[1:-1])


class PhotoNode(template.Node):
    def __init__(self, photo, photosize, css_class):
        self.photo = photo
        self.photosize = photosize
        self.css_class = css_class

    def render(self, context):
        try:
            a = template.resolve_variable(self.photo, context)
        except:
            a = self.photo
        if isinstance(a, Photo):
            p = a
        else:
            try:
                p = Photo.objects.get(slug=a)
            except Photo.DoesNotExist:
                # Ooops. Fail silently
                return None
        if not p.is_public:
            return None
        func = getattr(p, "get_%s_url" % (self.photosize), None)
        if func is None:
            return 'A "%s" photo size has not been defined.' % (self.photosize)
        else:
            return u'<img class="%s" src="%s" alt="%s" />' % (
                self.css_class,
                func(),
                p.title,
            )
