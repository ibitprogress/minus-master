# -*- coding: utf-8 -*-
import os
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django.views.decorators.cache import cache_page, never_cache
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import login
from django.contrib.contenttypes.models import ContentType

from users.models import UserProfile, StaffTicket
from users.forms import UserProfileEditForm, BlockUserForm, StaffTicketForm



@never_cache
@login_required
def user_editprofile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        instance = user.get_profile()
        if request.method == 'POST':
            form = UserProfileEditForm(request.POST, request.FILES,
                                       instance=instance)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.save()
                return redirect('user_profile', slug=user.username)
        else:
            form = UserProfileEditForm(instance=instance)
        return render_to_response('users/user_editprofile.html',
                                  {'form': form},
                                 context_instance=RequestContext(request))
    raise Http404

@never_cache
@login_required
def ban_user(request, id):
    """Viev for moderators ban_user"""
    
    if not request.user.is_staff:
        raise Http404

    user = get_object_or_404(User, id = id)
    profile = user.get_profile()
    message = ''
    if profile.banned:
        profile.banned = False
        profile.save()
    else:
        form = BlockUserForm(request.POST or None)
        if form.is_valid():
            profile.banned_until = request.POST['banned_until']
            message = request.POST['message']
            profile.banned = True
            profile.save()
            send_mail('minus.lviv.ua - акаунт заблоковано', u"""
Доброго дня.
Ваш акаунт (%s) на сайті minus.lviv.ua було тимчасово відключено
в зв’язку з порушенням правил користування ресурсом.

Причина: %s

Бан триває до %s
--------------------
minus.lviv.ua
                """ % (profile.fullname(),
                    message, 
                    profile.banned_until),
                settings.DEFAULT_FROM_EMAIL,
                [profile.user.email], fail_silently = False)
        else:
            form.initial = {'banned_until':\
                datetime.date.today()+datetime.timedelta(days=30),}
            return render_to_response('users/ban_user.html',
                                  {'form': form, 'user':profile.user},
                                 context_instance=RequestContext(request))
    return redirect(profile.get_absolute_url())



@cache_page(60*20)
def get_avatar(request, username):
    """
    shortcut mainly for easing acces via popup-menus
    when in JS we have only username
    """
    try:
        user = User.objects.get(username=username)
        file = user.get_profile().avatar.file
    except:
        file = open(os.path.join(settings.MEDIA_ROOT, "avatars", "default.png"))
    ext = file.name.split('.')[-1]
    return HttpResponse(file, mimetype="image/"+ext)
        

def search(request):
    if request.GET:
        search_term = '%s' % request.GET['q']
        cleaned_search_term = search_term.strip()
        if len(cleaned_search_term) != 0:
            if ' ' in cleaned_search_term:
                st_1 = cleaned_search_term.split(' ')[0]
                st_2 = cleaned_search_term.split(' ')[1]
                users = User.objects.filter(Q(first_name__icontains=st_1) |
                                                   Q(last_name__icontains=st_2) |
                                                   Q(first_name__icontains=st_2) |
                                                   Q(last_name__icontains=st_1) |
                                                   Q(username__icontains=st_1)|
                                                   Q(username__icontains=st_2)
                                                   )
            else:
                users = User.objects.filter(Q(first_name__icontains=cleaned_search_term) |
                                                  Q(last_name__icontains=cleaned_search_term)|
                                                  Q(username__icontains=cleaned_search_term))
            context = {'user_list': users, 'search_term': search_term}
        else:
            message = u'Помилка. Мабуть ви задали невірні параметри для пошуку.'
            context ={'message': message}
    else:
        return HttpResponseRedirect(reverse('user_list'))
    
    return render_to_response('users/user_list.html',
                             context,
                             context_instance=RequestContext(request))
@csrf_exempt
def quick_login(request):
    """
    hack to disable csrf on login.
    because, when user opens site first time, there is no csrf and session cookies
    """
    setattr(request, '_dont_enforce_csrf_checks', True)
    q_login = csrf_exempt(login)
    return q_login(request)


def submit_staff_ticket(request):
    """submitet via ajax form"""
    if request.is_ajax and request.method == 'POST':
        data = dict()
        
        data['user'] = str(request.user.id)
        data['url'] = request.POST['url']
        data['message'] = request.POST['message']
        data['object_id'] = int(request.POST['object_id'])
        url =''
        for s in request.POST['url'].split('/')[3:]:
            url+='/'+s
        url_func_name = resolve(url)[0].__name__
        # get function name
        if 'minus' in url_func_name:
            ct = ContentType.objects.get(app_label = 'minusstore',
                model = 'minusrecord')
            data['content_type'] = str(ct.id)
        st = StaffTicketForm(data )
        if st.is_valid():
            st.save()

        
        return HttpResponse("ok")
    else:
        raise Http404
