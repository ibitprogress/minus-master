import datetime
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, update_object,delete_object
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils import simplejson
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User

from models import Blurb, GeoRegion
from forms import BlurbForm, BlurbFilterForm

def blurb_add(request):
    return create_object(
        request,
        form_class = BlurbForm,
        login_required = True,
        template_name = 'blurbs/blurbs_add_edit.html',
        )

def blurb_edit(request, id):
    return update_object(
        request,
        object_id = id,
        form_class = BlurbForm,
        login_required = True,
        extra_context = {'edit':True,},
        template_name = 'blurbs/blurbs_add_edit.html',
        )

def blurbs_filter(request):
    get = request.GET
    if not 'category' in get: category = 'all'
    else: category = get['category'] 
        
    if not 'buysell' in get: buysell = 'A'
    else: buysell = get['buysell'] 

    if not 'georegion' in get: georegion = None
    else: georegion = get['georegion'] 

    if not 'geocity' in get: geocity = None
    else: geocity = get['geocity'] 
        
    if not 'unseen' in get: unseen = False
    else: unseen = True
        
    blurbs = Blurb.objects.all()
    form = BlurbFilterForm({
        'category':category,
        'buysell':buysell,
        'georegion': georegion,
        'geocity': geocity,
        'unseen':unseen
        })


    sessionkey = 'seen_blurbs_%s' % category
    if unseen and request.session.has_key(sessionkey):
        blurbs = blurbs.filter(pub_date__gte = request.session[sessionkey])
    if not category == 'all':
        blurbs = blurbs.filter(category__slug__iexact = category)
    if not buysell == 'A':
        blurbs = blurbs.filter(buysell = buysell)
    if georegion:
        blurbs = blurbs.filter(georegion__id = georegion)
    if geocity:
        blurbs = blurbs.filter(geocity__id = geocity)

    request.session[sessionkey] = datetime.datetime.now()
    return object_list(
        request,
        queryset = blurbs,
        extra_context = {'form':form},
        template_name = 'blurbs/blurbs_filter.html',
    )
    

def blurbs_by_user(request, username):
    user = get_object_or_404(User, username = username)
    return object_list(
        request,
        queryset = Blurb.objects.filter(user = user),
        extra_context = {'blurb_user':user},
        template_name = 'blurbs/blurbs_filter.html'
        )

def blurb_detail(request, category,buysell, id):
    return object_detail(
        request,
        queryset = Blurb.objects.all(),
        object_id = id,
        template_name = 'blurbs/blurb_detail.html',
        )
    

def blurb_delete(request, id):
    return delete_object(
        request,
        model = Blurb,
        object_id = id,
        post_delete_redirect = reverse('blurbs_filter'),
        login_required = True,
        template_name = 'shared/object_delete_confirm.html',
        )

def geoinfo(request, id):
    region = get_object_or_404(GeoRegion, id = id)
    
    data = region.geocity_set.all().values_list('id','title')
    return HttpResponse(simplejson.dumps(list(data)),
        content_type = 'application/json')


def blurb_up(request, id):
    blurb = get_object_or_404(Blurb,id = id)
    if request.is_ajax() and\
    (request.user == blurb.user or request.user.is_staff) and\
    blurb.pub_date < datetime.datetime.now() - datetime.timedelta(days = 7):
        blurb.pub_date = datetime.datetime.now()
        blurb.save()
        return HttpResponse("OK")
    else:
        raise Http404
