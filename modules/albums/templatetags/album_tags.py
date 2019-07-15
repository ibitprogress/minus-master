import re

from django.core.urlresolvers import reverse
from django import template
from django.conf import settings
from django.contrib.auth.models import User

from albums.models import Audio

register = template.Library()




@register.inclusion_tag('albums/album_audio.html')
def render_audio_album_for(user,request=None):
    objects = Audio.objects.filter(user = user)
    return {'objects':objects,'request':request, 'MEDIA_URL':settings.MEDIA_URL}
