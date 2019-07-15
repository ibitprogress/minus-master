# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from links.forms import FriendLinkAddForm
from links.models import FriendLinkCategory

def links_list(request, *args, **kwargs):   #hack due to production server bug
    categories = FriendLinkCategory.objects.all()
    return render_to_response('links/links_list.html',
                              {'categories': categories},
                             context_instance=RequestContext(request))

def links_add(request, *args, **kwargs):
    if request.method == 'POST':
        form = FriendLinkAddForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.save()

            return render_to_response('links/links_added.html',
                                      {'link': link},
                                     context_instance=RequestContext(request))
    else:
        form = FriendLinkAddForm()

    return render_to_response('links/links_add.html',
                              {'form': form},
                             context_instance=RequestContext(request))
