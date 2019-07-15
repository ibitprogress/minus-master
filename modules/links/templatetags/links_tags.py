from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def edit_object(obj):
    """
    Return a link for editing object in admin site
    """
    return reverse('admin:%s_%s_change' % (obj._meta.app_label,
                                           obj._meta.module_name),
                                           args=(obj.id,))
