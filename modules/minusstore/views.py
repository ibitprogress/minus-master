# -*- coding: utf-8 -*-

import sys
import datetime
from django.conf import settings

from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.sessions.models import Session
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.views.generic.create_update import delete_object
from django.core.urlresolvers import reverse

from minusstore.forms import UploadForm, MinusPlusForm
from minusstore.models import MinusRecord, MinusAuthor, FileType, MinusCategory, MinusStats, CommentNotify, MinusPlusRecord

from django_inlines import inlines
from django_inlines.samples import YoutubeInline

from forum.decorators import confirm_required #TODO replace with delete_object
from minusstore.utils import allowed_extensions
from users.models import create_rating
from hitcount.models import HitCount
from hitcount.views import _update_hit_count
from albums.models import Audio,AudioAlbum

inlines.registry.register('youtube', YoutubeInline)


@never_cache
@csrf_exempt
def minus_flash_upload(request):
    """
    Backend view for recieving file and form-data from 
    asynchronus uploader(swfup)

    it's not covered by default csrf mechanism, because
    flash uploader does not send browser's cookies
    
    it's able to re-implement csrf by hands, but
    it's not so hardly needed

    so only session-tokens

    """

    if request.method == 'POST':
        s = get_object_or_404(Session, pk=request.POST['session_key'])
        if '_auth_user_id' in s.get_decoded():  #custom auth-validation
            user = get_object_or_404 (User, id = s.get_decoded()['_auth_user_id'])
            request.POST['user'] = user.id
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                file_obj = form.save()
                create_rating(sender = MinusRecord, instance = file_obj.user) #call signal to recoutn rating
                return HttpResponse(file_obj.get_absolute_url())
            else:
                err = form.errors.as_text()
                #do errors formatting. it would be better to do it by
                #redefining method in form. But i'm lazy today
                newerr = '<div class="errorlist">'
                for line in err.split('\n'):
                    if  line.startswith("*")\
                    and not line.startswith("* __all__"):
                        pass
                    elif line.startswith("  "):
                        newerr += line+"<br/>"
                newerr +="</div>"
                return HttpResponse(newerr)
            raise Http404
    else:
        return redirect('minus_upload') 


@never_cache
@login_required
def minus_upload(request):
    initial = {'user':request.user.pk}
    form = UploadForm(initial=initial)

    if request.method == 'POST':
        if request.POST.has_key('__confirm__'):  #we are submiting agreement form
            request.POST = {}
            request.method = 'GET'
            request.user.get_profile().seen_rules = True
            request.user.get_profile().save()
        else:
            if request.POST['user'] != str(request.user.id): request.POST['user'] = str(request.user.id)
            form = UploadForm(request.POST, request.FILES, initial=initial)
            if form.is_valid():
                file_obj = form.save()
                return redirect(file_obj)

    else:
        if not request.user.get_profile().seen_rules:
            try:
                f = FlatPage.objects.get(url='/rules/')
                return render_to_response('flatpages/agree.html',
                    {'flatpage':f},
                    context_instance=RequestContext(request))
            except FlatPage.DoesNotExist:
                pass
            

    return render_to_response('minusstore/upload.html',
        {'form':form,
        'exts':allowed_extensions()}, 
        context_instance=RequestContext(request))

@csrf_exempt
@never_cache
def minus_mass_upload(request):
    """Multiple file upload via flash uploader"""

    if request.method == 'POST':
        
        # Manually get session and check is user authenticated
        # The key is provided by flash uploader
        s = get_object_or_404(Session, pk=request.POST['session_key'])
        if '_auth_user_id' in s.get_decoded():
            user = get_object_or_404 (User, id = s.get_decoded()['_auth_user_id'])
            #hack with hardcoded initial data. Somewhy it is not loaded
            #from model field-defitinions
            initial = {'user':user.pk, 'gender':"all", 'tempo':"normal", 'staff':"solo"}
            form = UploadForm(initial, request.FILES,  initial=initial)
            if form.is_valid():
                file_obj = form.save()
                create_rating(sender = MinusRecord, instance = file_obj.user) #call signal to recoutn rating
                return HttpResponse("Ok")
            else:
                resp =  HttpResponse("Bad Data")
                resp.status_code = 403
                return resp
        else:
            raise Http404

    else:
        if not request.user.is_authenticated():
            #also manual checking for is_authenticated
            raise Http404
        exts = allowed_extensions()
    return render_to_response('minusstore/mass_upload.html',{'exts':exts}, 
        context_instance=RequestContext(request))

@never_cache
@login_required
def minus_edit(request, user, id):
    minus = get_object_or_404(MinusRecord,  id = int(id))
    if request.user != minus.user and not request.user.is_staff:
        raise Http404
    initial = {'user':minus.user.pk,
        'author':minus.author.name
        }

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, instance=minus, initial=initial, edit=True)
        if form.is_valid():
            file_obj = form.save()
            return redirect(file_obj)

    else:
        form = UploadForm(initial=initial, instance=minus)

    return render_to_response('minusstore/upload.html', {'form':form, 'edit':True, 'instance':minus}, 
        context_instance=RequestContext(request))

@never_cache
@login_required
def plus_upload(request, user = None):
    if not user: user = str(request.user.id) 
    if request.method == 'POST':
        form = MinusPlusForm({'user':user},request.FILES )
        if form.is_valid():
            form.save()
            return redirect('minus_plus_upload_done')
    else:
        form = MinusPlusForm()
    
    return render_to_response('minusstore/plus_upload.html', {'form':form}, 
        context_instance=RequestContext(request))

def plus_upload_done(request):
    """docstring for plus_upload_done"""
    try:
        f = FlatPage.objects.get(url=request.path)
        return render_to_response('flatpages/default.html',
            {'flatpage':f},
            context_instance=RequestContext(request))
    except FlatPage.DoesNotExist:
        return redirect('minus_by_user', request.user.username)
    
@never_cache
def plus_delete(request,id):
    plus = get_object_or_404(MinusPlusRecord, id = id)
    if plus.user == request.user or request.user.is_staff:
        return delete_object(
            request,
            model = MinusPlusRecord,
            object_id = id,
            post_delete_redirect = reverse('minus_by_user', 
                args=[request.user.username]),
            extra_context = {'object_name':u'плюсовку'},
            template_name = 'shared/object_delete_confirm.html',
            )

    
    

def minus_delete_context(request, user, id):
    minus = get_object_or_404(MinusRecord,  id = int(id))
    if request.user != minus.user and not request.user.is_staff:
        raise Http404
    return RequestContext(request, { 'minus': minus })

@login_required
@confirm_required('minusstore/minus_delete_confirm.html', minus_delete_context)
def minus_delete(request, user, id):
    minus = get_object_or_404(MinusRecord,  id = int(id))
    if request.user != minus.user and not request.user.is_staff:
        raise Http404
    let = unicode(minus.author)[0].upper()
    minus.delete()
    return redirect('minus_author_by_letter', let)


@cache_page(60*20)
def minus_index(request):
    """
    displays latest arived records
    """
    minuses = MinusRecord.objects.all()
    return render_to_response('minusstore/date_archive.html', {'minuses':minuses}, 
        context_instance=RequestContext(request))

@cache_page(60*20)
def minus_by_type(request, type):
    min_type =  get_object_or_404(FileType,type_name = type)
    types = FileType.objects.all()
    minuses = min_type.matched_records.all()
    return render_to_response('minusstore/by_type.html', {'minuses':minuses, 'type':min_type, 'types':types}, 
        context_instance=RequestContext(request))

@cache_page(60*5)
def minus_by_author(request, author, ajax = False, type = '', letter = '', t_class = ''):
    min_author = get_object_or_404(MinusAuthor,name = author)
    minuses = min_author.records_by.all().order_by('title')
    if type:
        minuses = minuses.filter(type__type_name__exact = type)
    if letter:
        if letter == "0-9":
            minuses = minuses.filter(title__regex = r'^[0-9].*$')
        else:
            minuses = minuses.filter(title__istartswith = letter)
    
    if t_class:
        if t_class == 'alternative': minuses = minuses.filter(alternative = True)
        else: minuses = minuses.filter(alternative = False)
    if ajax:
        return render_to_response('minusstore/ajax_author.html',{'minuses':minuses},
            context_instance=RequestContext(request))
    else:
        return render_to_response('minusstore/by_author.html',
                {'minuses':minuses,
                'author':min_author,
                }, 
        context_instance=RequestContext(request))


@cache_page(60*15)
def minus_author_by_letter(request, letter=u"А"):
    """
    get author by specified letter 
    if no letter, get all authors
    also get folk-songs, which names
    starting from specified letter
    """

    folk_minuses = MinusRecord.objects.filter(is_folk = True)
    if letter:
        if letter == "0-9":
            authors = MinusAuthor.objects.filter(name__iregex = r'^[0-9].*$')
            folk_minuses = folk_minuses.filter(title__iregex = r'^[0-9].*$')
        else:
            authors = MinusAuthor.objects.filter(name__istartswith = letter).order_by('name')
            folk_minuses = folk_minuses.filter(title__istartswith = letter)

    else:
            authors = MinusAuthor.objects.all()
    types = FileType.objects.all()
    categories = MinusCategory.objects.all()
    return render_to_response('minusstore/author_index.html',
            {'authors':authors,
            'folk_minuses':folk_minuses,
            'letter':letter,
            'categories':categories,
            'types':types,
            }, 
        context_instance=RequestContext(request))

@cache_page(60*5)
def minus_detail(request, author, id):
    minus = get_object_or_404(MinusRecord,  id = int(id))
    return render_to_response('minusstore/minus_detail.html', {'object':minus}, 
        context_instance=RequestContext(request))

@login_required
def minus_download(request, author, id):
    minus = get_object_or_404(MinusRecord,  id = int(id))
    hitcount,c = HitCount.objects.get_or_create(object_pk = minus.pk,
        content_type = ContentType.objects.get_for_model(MinusRecord))

    if _update_hit_count(request, hitcount):
        stat,c = MinusStats.objects.get_or_create(minus = minus,
            date=datetime.date.today)
        stat.rate = F('rate') + 1
        stat.save()
        minus.rating.score += 1
        minus.save()
        create_rating(sender = MinusRecord, instance = minus.user) #call signal to recount rating
    return redirect(minus.file.url, permanent = True) #attachment is handled by ngnix

@cache_page(60*20)
def minus_time_archive(request, year , month = None, day = None):
    year = int(year) 
    if year < 2008 or year > datetime.datetime.now().year+1:
        raise Http404
    minuses = MinusRecord.objects.filter(pub_date__year = year)
    nextyear = year+1
    prevyear = year-1
    if month:
        month = int(month)
        nextmonth = month+1     #silly:D
        if nextmonth > 12:
            nextmonth = 1
        prevmonth = month-1
        if prevmonth < 1:
            prevmonth = 12
        minuses = minuses.filter(pub_date__month = month)
        
        if day:
            day = int(day)
            minuses = minuses.filter(pub_date__day = day)
            day = datetime.datetime(year, month, day)
    
        try:
            month = datetime.datetime(year, month, 1) #here because we pass
                                                  #an int to datetime.month
        except ValueError:
            raise Http404
        context = {'minuses':minuses,
        'year':year,
        'month':month,
        'day':day,
        'nextmonth':nextmonth,
        'prevmonth':prevmonth,
        'nextyear':nextyear,
        'prevyear':prevyear,
        }

    else:
        context = {'minuses':minuses,
        'year':year,
        'nextyear':nextyear,
        'prevyear':prevyear,
        }
            
    return render_to_response('minusstore/date_archive.html', context,
        context_instance=RequestContext(request))

    
@cache_page(60*20)
def minus_by_user(request, username):
    user = get_object_or_404(User, username = username)
    minuses = MinusRecord.objects.filter(user = user)
    return render_to_response('minusstore/by_user.html',{'minuses':minuses, 'user':user,},
        context_instance=RequestContext(request))

def comments_for(request, username):
    """
    display comments for minuses uploaded by user
    """

    user = get_object_or_404(User, username = username)
    comments = CommentNotify.objects.filter(user = user).order_by('-pk') #no date, my fuckup
    for comment in comments.filter(is_seen = False):
        comment.is_seen = True
        comment.save()
    return render_to_response('minusstore/comments_for.html', 
        {'comments':comments, 'user':user,},
        context_instance=RequestContext(request))


def convert_context_minus(request,id):
    minus = get_object_or_404(MinusRecord, id = id)
    return RequestContext(request,{'object':minus,'type':'minus'})
    

@login_required
@confirm_required('minusstore/confirm_convert.html', convert_context_minus)
def minus_to_audiorec(request, id):
    minus = get_object_or_404(MinusRecord, id = id)
    #could be done by decorator FIXME
    if request.user != minus.user and not request.user.is_staff:  
        raise Http404
    audiorec = Audio(user = minus.user, 
        title = minus.__unicode__(),
        description = minus.annotation,
        pub_date = minus.pub_date
        )
    audiorec.file.save(minus.file.name.split('/')[-1],
        minus.file.file)
    audiorec.save()
    minus.delete()
    return redirect(audiorec.get_absolute_url())

def convert_context_audiorec(request,id):
    audio = get_object_or_404(Audio, id = id)
    return RequestContext(request,{'object':audio,'type':'audio'})

@login_required
@confirm_required('minusstore/confirm_convert.html', convert_context_audiorec)
def audiorec_to_minus(request, id):
    audiorec = get_object_or_404(Audio, id = id)
    if request.user != audiorec.user and not request.user.is_staff:  
        raise Http404
    initial = {'user':audiorec.user.pk, 'gender':"all",
        'tempo':"normal", 'staff':"solo", 'alternative':True,
        'file':audiorec.file.file}
    form = UploadForm(initial,initial=initial)
    if form.is_valid():
        minus = form.save()
        audiorec.delete()
        
        #call signal to recoutn rating
        create_rating(sender = MinusRecord, instance = minus.user) 
        return redirect('minus_edit', user=minus.user.username, id=str(minus.id))
    else:
        return HttpResponse("not ok")

    
