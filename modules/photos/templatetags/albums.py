import re

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django import template
from django.conf import settings

from photos.models import PhotoAlbum

register = template.Library()
 

@register.simple_tag
def get_album_url_for_obj(object):
    ct = ContentType.objects.get_for_model(object)
    try:
        album = PhotoAlbum.objects.get(content_type = ct, object_pk = object.pk,
            user = object.user)
        return reverse('album_detail', args=[album.slug])
    except PhotoAlbum.DoesNotExist:
        return ''
        

@register.inclusion_tag('photos/album_photo.html')
def render_photo_album_for(object):
    ct = ContentType.objects.get_for_model(object)
    try:
        album = PhotoAlbum.objects.get(content_type = ct, object_pk = object.pk,
        user = object.user)
    except PhotoAlbum.DoesNotExist:
        album = None
        
    return {'album':album, 'MEDIA_URL':settings.MEDIA_URL}


class CoverPhotoNode(template.Node):
    def __init__(self,object, var_name = 'cover_photo'):
        self.object = template.Variable(object)
        self.var_name = var_name

    def render(self, context):
        obj = self.object.resolve(context)
        ct = ContentType.objects.get_for_model(obj)
        try:
            album = PhotoAlbum.objects.get(content_type = ct, object_pk = obj.pk)
            context[self.var_name] = album.get_cover_photo()
        except PhotoAlbum.DoesNotExist:
            context[self.var_name] = ''
        return ''

@register.tag('get_cover_photo')
def get_cover_photo(parser, token):
    """Return url to photo, if object has photo album"""
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, arg = token.contents.split(None, 1)

    except ValueError:
        raise template.TemplateSyntaxError,\
        "%r tag requires a single argument" % token.contents.split()[0]
    m = re.search(r'for (.*?) as (\w+)', arg)
    object, var_name = m.groups()
    return CoverPhotoNode(object, var_name)
