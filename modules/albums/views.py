# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.generic.create_update import create_object, update_object,delete_object
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


from models import Audio, AudioAlbum, create_album_for
from forms import AudioForm, AudioAlbumForm

models = {'audio':Audio}
albummodels = {'audio':AudioAlbum}
albumforms = {'audio':AudioAlbumForm}
forms = {'audio':AudioForm}

@login_required
def up_object(request, type, username, album = None):
    """upload audio to album attached to the object"""
    user = get_object_or_404(User, username = username)

    if album:
        album = get_object_or_404(albummodels[type],slug = album)
    if request.method == 'POST': 
        form = forms[type](request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            return redirect(obj)
    else:
        form = forms[type](initial = {'user':user.pk, 'album':album})
    template_name = 'albums/up_%s.html' % type

    return direct_to_template(request,template_name,{'form':form})

@login_required
def show_objects(request, type, username, album = None):
    """edit album attached to the object"""

    user = get_object_or_404(User, username = username)
    if album:
        album= get_object_or_404(albummodels[type], user = user, slug = album)
        objects = album.audio_set.all()
    else:
        model = models[type]                    #model of album
        album = user
        objects = model.objects.filter(user__username  = username) #album actually

    template_name = 'albums/list_%s.html' % type

    return object_list(
        request,
        queryset = objects,
        template_name = template_name,
        extra_context = {'album':album,},

        )



@login_required
def edit_object(request, type, instance_pk):
    """
    edit object
    """
    form = forms[type]
    template_name = 'albums/up_%s.html' % type
    return update_object(
        request,
        object_id = instance_pk,
        form_class = form,
        login_required = True,
        extra_context = {'edit':True,},
        template_name = template_name,
        )


@login_required
def remove_object(request,type, username, instance_pk):
    """
    not using term delete to avoid collisions
    """
    modelclass = models[type]   #avoid collisions again
    obj = modelclass.objects.get(pk = instance_pk)
    if obj.user != request.user: raise Http404
    return delete_object(
        request,
        model = modelclass,
        object_id = instance_pk,
        login_required = True,
        post_delete_redirect = reverse('show_objects',args=[type,username]),
        extra_context = {'object_name':'об’єкт'},
        template_name = 'shared/object_delete_confirm.html',
        )

@login_required
def create_album(request, type, username):
    form = albumforms[type](request.POST or None)
    template_name = 'albums/create_album_%s.html' % type
    if form.is_valid():
        obj = form.save(commit = False) #get an unbound object
        obj.content_type = ContentType.objects.get_for_model(obj.user)
        obj.object_pk = obj.user.pk
        obj.save()
        return redirect('up_object_to_album', type, username, obj.slug)

    return direct_to_template(request,template_name,{'form':form})
@login_required
def edit_album(request,type,username, instance_pk):
    form = albumforms[type]
    template_name = 'albums/create_album_%s.html' % type
    return update_object(
        request,
        object_id = instance_pk,
        form_class = form,
        login_required = True,
        extra_context = {'edit':True,},
        template_name = template_name,
        )
    
@login_required
def remove_album(request,type,username,instance_pk):
    modelclass = albummodels[type]
    obj = modelclass.objects.get(pk = instance_pk)
    if obj.user != request.user: raise Http404
    return delete_object(
        request,
        model = modelclass,
        object_id = instance_pk,
        login_required = True,
        post_delete_redirect = reverse('list_albums',args=[type,username]),
        extra_context = {'object_name':'альбом'},
        template_name = 'shared/object_delete_confirm.html',
        )

def show_album(request,type, username, slug):
    """utilitary view for showing audio album via templatetag"""
    user = get_object_or_404(User, username = username)
    album = get_object_or_404(albummodels[type], user = user, slug = slug)
    template_name = 'albums/%s_album.html' % type
    return direct_to_template(request ,template_name,
                          {'album':album})
                         
def show_object_detail(request,type, username, slug, instance_pk):
    user = get_object_or_404(User, username = username)
    return object_detail(request, 
        queryset = models[type].objects.all(),
        object_id = instance_pk,
        template_name = 'albums/%s_detail.html' % type,
        )


def list_albums(request, type, username):
    user = get_object_or_404(User, username = username)
    albums = albummodels[type].objects.filter(user__username = username)
    return direct_to_template( request, 'albums/list_%s_albums.html' % type,
    {'object_list':albums, 'album_user':user})
