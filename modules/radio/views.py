import urllib
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.conf import settings 
from django.contrib.flatpages.models import FlatPage


def radio_page(request):
    try:
        f = FlatPage.objects.get(url="/radio/")
    except FlatPage.DoesNotExist:
        f = ''
    return render_to_response('radio/radio.html',
        {'flatpage':f },
        context_instance = RequestContext(request))


def radio_status(request):
    status = "DEAD"
    try:
        r = urllib.urlopen(settings.RADIO_URL)
        if r.getcode() == 200:
            status = "OK"
    except IOError:
        pass
    return HttpResponse(status)


