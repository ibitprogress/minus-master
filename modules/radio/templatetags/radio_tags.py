from django.conf import settings
from django import template

register = template.Library()

@register.inclusion_tag('radio/radio_widget.html')
def radio_widget():
    """
    Show radio widget
    """
    return {'RADIO_URL': settings.RADIO_URL,
    'MEDIA_URL':settings.MEDIA_URL}
