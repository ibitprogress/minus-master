"""
All forum logic is kept here - displaying lists of forums, threads 
and posts, adding new threads, and adding replies.
"""

from django.contrib.auth.models import User
from datetime import datetime
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden, HttpResponseNotAllowed
from django.template import RequestContext, Context, loader
from django import forms
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.defaultfilters import striptags, wordwrap
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from forum.models import Forum,Thread,Post,Subscription
from forum.forms import CreateThreadForm, ReplyForm, ThreadEditForm, PostEditForm
from forum.decorators import confirm_required

FORUM_PAGINATION = getattr(settings, 'FORUM_PAGINATION', 10)
LOGIN_URL = getattr(settings, 'LOGIN_URL', '/accounts/login/')

def forums_list(request):
    queryset = Forum.objects.for_groups(request.user.groups.all()).filter(parent__isnull=True)
    return object_list( request,
                        queryset=queryset)

def forum(request, slug):
    """
    Displays a list of threads within a forum.
    Threads are sorted by their sticky flag, followed by their 
    most recent post.
    """
    try:
        f = Forum.objects.for_groups(request.user.groups.all()).select_related().get(slug=slug)
    except Forum.DoesNotExist:
        raise Http404
    
    forums = Forum.objects.all()
    form = CreateThreadForm()
    child_forums = f.child.for_groups(request.user.groups.all())
    return object_list( request,
                        queryset=f.thread_set.select_related().all(),
                        template_object_name='thread',
                        template_name='forum/thread_list.html',
                        extra_context = {
                            'forum': f,
                            'child_forums': child_forums,
                            'form': form,
                            'forums': forums,
                        })

def thread(request, thread):
    """
    Increments the viewed count on a thread then displays the 
    posts for that thread, in chronological order.
    """
    try:
        t = Thread.objects.select_related().get(pk=thread)
        if not Forum.objects.has_access(t.forum, request.user.groups.all()):
            raise Http404
    except Thread.DoesNotExist:
        raise Http404
    
    forums = Forum.objects.all()
    p = t.post_set.select_related('author').all().order_by('time')
    s = None
    if request.user.is_authenticated():
        s = t.subscription_set.select_related().filter(author=request.user)

    t.views += 1
    t.save()

    if s:
        initial = {'subscribe': True}
    else:
        initial = {'subscribe': False}

    form = ReplyForm(initial=initial)

    
    return object_list( request,
                        queryset=p,
                        template_object_name='post',
                        template_name='forum/thread.html',
                        extra_context = {
                            'forum': t.forum,
                            'forums': forums,
                            'thread': t,
                            'subscription': s,
                            'form': form,
                        })

def reply(request, thread):
    """
    If a thread isn't closed, and the user is logged in, post a reply
    to a thread. Note we don't have "nested" replies at this stage.
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (LOGIN_URL, request.path))
    t = get_object_or_404(Thread, pk=thread)
    if t.closed:
        return HttpResponseServerError()
    if not Forum.objects.has_access(t.forum, request.user.groups.all()):
        return HttpResponseForbidden()

    subscript = Subscription.objects.filter(thread=t, author=request.user)
    global initial
    initial = {'body': ' ', 'subscribe': True}

    if request.method == "POST":
        if subscript:
            form = ReplyForm(request.POST, initial)
        else:
            form = ReplyForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']
            p = Post(
                thread=t, 
                author=request.user,
                body=body,
                time=datetime.now(),
                )
            p.save()

            sub = Subscription.objects.filter(thread=t, author=request.user)
            if form.cleaned_data.get('subscribe',False):
                if not sub:
                    s = Subscription(
                        author=request.user,
                        thread=t
                        )
                    s.save()
            else:
                if sub:
                    sub.delete()

            if t.subscription_set.count() > 0:
                # Subscriptions are updated now send mail to all the authors subscribed in
                # this thread.
                mail_subject = ''
                try:
                    mail_subject = settings.FORUM_MAIL_PREFIX 
                except AttributeError:
                    mail_subject = '[Forum]'

                mail_from = ''
                try:
                    mail_from = settings.FORUM_MAIL_FROM
                except AttributeError:
                    mail_from = settings.DEFAULT_FROM_EMAIL

                mail_tpl = loader.get_template('forum/notify.txt')
                c = Context({
                    'body': wordwrap(striptags(body), 72),
                    'site' : Site.objects.get_current(),
                    'thread': t,
                    })

                recipients = [s.author.email for\
                        s in t.subscription_set.exclude(author = request.user)]
                email = EmailMessage(
                        subject=mail_subject+' '+striptags(t.title),
                        body= mail_tpl.render(c),
                        from_email=mail_from,
                        bcc=recipients,)
                email.send(fail_silently=True)

            return HttpResponseRedirect(p.get_absolute_url())
            
    else:
        if subscript:
            form = ReplyForm(initial)
        else:
            form = ReplyForm()
    
    return render_to_response('forum/reply.html',
        RequestContext(request, {
            'form': form,
            'forum': t.forum,
            'thread': t,
        }))


def newthread(request, forum):
    """
    Rudimentary post function - this should probably use 
    newforms, although not sure how that goes when we're updating 
    two models.

    Only allows a user to post if they're logged in.
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (LOGIN_URL, request.path))

    f = get_object_or_404(Forum, slug=forum)
    
    if not Forum.objects.has_access(f, request.user.groups.all()):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CreateThreadForm(request.POST)
        if form.is_valid():
            t = Thread(
                forum=f,
                title=form.cleaned_data['title'],
            )
            t.save()

            p = Post(
                thread=t,
                author=request.user,
                body=form.cleaned_data['body'],
                time=datetime.now(),
            )
            p.save()
    
            if form.cleaned_data.get('subscribe', False):
                s = Subscription(
                    author=request.user,
                    thread=t
                    )
                s.save()
            return HttpResponseRedirect(t.get_absolute_url())
    else:
        form = CreateThreadForm()

    return render_to_response('forum/newthread.html',
        RequestContext(request, {
            'form': form,
            'forum': f,
        }))

@login_required
def threadedit(request, thread):
    """
    Allows moderators to edit threads
    """
    user = get_object_or_404(User, pk=request.user.pk)
    thread_id = int(thread)
    instance = get_object_or_404(Thread, id=thread_id)
    if user.is_staff:
        if request.method == 'POST':
            form = ThreadEditForm(request.POST, instance=instance)
            if form.is_valid():
                thread = form.save(commit=False)
                thread.save()
                return redirect('forum_view_thread', thread=thread_id)
        else:
            form = ThreadEditForm(instance=instance)

        return render_to_response('forum/threadedit.html',
                                  {'form': form,
                                   'thread': instance},
                                  context_instance=RequestContext(request))

    # TODO: Make a proper action when someone is trying to edit thread
    # without moderator permission
    return HttpResponse('Not a moderator')

@login_required
def postedit(request, post):
    """
    Allows moderators and owners to edit posts
    """
    user =  get_object_or_404(User, pk=request.user.pk)
    post_id = int(post)
    instance = get_object_or_404(Post, id=post_id)
    thread_id = instance.thread.id
    if user.is_staff or user == instance.author:
        if request.method == 'POST':
            form = PostEditForm(request.POST, instance=instance)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect('forum_view_thread', thread=thread_id)
        else:
            form = PostEditForm(instance=instance)
        
        return render_to_response('forum/postedit.html',
                                  {'form': form,
                                   'thread':instance.thread },
                                 context_instance=RequestContext(request))

    # TODO: Make a proper action when someone is trying to edit thread
    # without moderator permission
    return HttpResponse('Not a moderator')


def threadremove_context(request, thread):
    thread_id = int(thread)
    thread = get_object_or_404(Thread, id=thread_id)
    return RequestContext(request, {'thread': thread})

@login_required
@confirm_required('forum/remove_confirm.html', threadremove_context)
def threadremove(request, thread):
    """
    Allows moderators to delete threads
    """
    user = get_object_or_404(User, pk=request.user.pk)
    thread_id = int(thread)
    thread = get_object_or_404(Thread, id=thread_id)
    forum_slug = thread.forum.slug
    if user.is_staff:
        thread.delete()
        return redirect('forum_thread_list', slug=forum_slug)

    # TODO: Make a proper action when someone is trying to edit thread
    # without moderator permission
    return HttpResponse('Not a moderator')

def postremove_context(request, post):
    post_id = int(post)
    post = get_object_or_404(Post, id=post_id)
    return RequestContext(request, {'post': post})

@login_required
@confirm_required('forum/remove_confirm_post.html', postremove_context)
def postremove(request, post):
    """
    Allows moderators to delete posts
    """
    user = get_object_or_404(User, pk=request.user.pk)
    post_id = int(post)
    post = get_object_or_404(Post, id=post_id)
    thread_id = post.thread.id
    if user.is_staff:
        post.delete()
        return redirect('forum_view_thread', thread=thread_id)

    # TODO: Make a proper action when someone is trying to edit thread
    # without moderator permission
    return HttpResponse('Not a moderator')



def updatesubs(request):
    """
    Allow users to update their subscriptions all in one shot.
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (LOGIN_URL, request.path))

    subs = Subscription.objects.select_related().filter(author=request.user)

    if request.POST:
        # remove the subscriptions that haven't been checked.
        post_keys = [k for k in request.POST.keys()]
        for s in subs:
            if not str(s.thread.id) in post_keys:
                s.delete()
        return HttpResponseRedirect(reverse('forum_subscriptions'))

    return render_to_response('forum/updatesubs.html',
        RequestContext(request, {
            'subs': subs,
            'next': request.GET.get('next')
        }))
       
