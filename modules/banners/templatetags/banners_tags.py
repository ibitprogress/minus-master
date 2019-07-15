import sys

import random
from django.conf import settings
from django import template
from banners.models import PlaceHolder, Banner

register = template.Library()

def get_banner(parser, token):
    """
    get banner by it's category(placeholder) and text-key
    if no text-key given: return random banner of specified category
    if no placeholder specified: return just random banner
    """

    tokens = token.split_contents()
    holder = '""'
    banner = '""' #quotes are stripped later

    if len(tokens) < 1 or len(tokens) > 3:
        raise template.TemplateSyntaxError, "%r tag should have from 1 to 3 arguments" % (tokens[0],)
    if len(tokens) == 2:
        tag_name, holder = tokens
    if len(tokens) == 3:
        tag_name, holder, banner = tokens
    # Check to see if the key is properly double/single quoted
    if not (holder[0] == holder[-1] and holder[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    if not (banner[0] == banner[-1] and banner[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return BannersNode(holder[1:-1],banner[1:-1])

class BannersNode(template.Node):
    """docstring for BannersNode"""
    def __init__(self, holder, banner):
        self.holder, self.banner = holder, banner

    def render(self, context):
        """
        render random banner of specified placeholder 
        (if placeholder not specified, it is also random)
        take some care of priority for displaying, but with great
        randomisation
        """
        placeholder = None
        if self.holder:
            try:
                placeholder = PlaceHolder.objects.get(key = self.holder)
            except:
                pass
                #raise template.TemplateSyntaxError, " could not find holder %s" % self.holder
        else:
            if PlaceHolder.objects.all():
                placeholder = PlaceHolder.objects.all()\
                [random.randint(0, PlaceHolder.objects.count()-1)] #random holder

        # get only banners for our placeholder
        content = ""

        if self.banner:
            try:
                bannerobj = Banner.objects.get(key = self.banner) #if we specify
                content = bannerobj.content
            except:
                if settings.DEBUG:
                    raise template.TemplateSyntaxError, " could not find banner %s" % self.banner


        else:
            banners = Banner.objects.filter(holder = placeholder)
            if banners:
                randm = random.randint(0,10)
                filt_banners = banners.filter(ratio__gte=randm) #higher ratio, higher chance
                if not filt_banners:
                    filt_banners = banners #but if no match, get just anything
                #get random banner of those who are left
                bannerobj = filt_banners[random.randint(0, len(filt_banners)-1)]
                content = u'''<div id="%s" class="banner">%s</div>
                ''' % (placeholder.key, bannerobj.content)
        return content


register.tag('banner', get_banner)
