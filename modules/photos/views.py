# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from forum.decorators import confirm_required

from photos.models import PhotoAlbum, Photo
from photos.forms import PhotoAlbumEditForm, PhotoAddForm, PhotoEditForm
from albums.models import create_album_for

def album_detail(request, album):
    """get by slug, or return for username
    
    if user requests his own album, create it
    """
    try:
        album = PhotoAlbum.objects.get(slug=album)
    except PhotoAlbum.DoesNotExist:
        try:
            album_user = User.objects.get(username = album)
            album = PhotoAlbum.objects.get(user = album_user, object_pk = album_user.get_profile().id)
        except (PhotoAlbum.DoesNotExist, User.DoesNotExist):
            if request.user == album_user:
                # using root function instead of signal
                album = create_album_for(album_user.get_profile(), album_user, PhotoAlbum)
            else:
                raise Http404

    return render_to_response('photos/album_detail.html',
                              { 'album': album },
                             context_instance=RequestContext(request))

def photo_detail(request, album, id):
    album = get_object_or_404(PhotoAlbum, slug=album)
    photo = get_object_or_404(Photo, id=int(id), album=album)
    
    return render_to_response('photos/photo_detail.html',
                              { 'photo': photo },
                             context_instance=RequestContext(request))

def album_index(request):
    albums = PhotoAlbum.albums.all()
    return render_to_response('photos/album_index.html',
                              { 'albums': albums },
                             context_instance=RequestContext(request))

@login_required
def album_edit(request, album):
    try:
        album = PhotoAlbum.objects.get(slug=album)
    except:
        raise Http404
    if request.user == album.user:
        instance = album
        if request.method == 'POST':
            form = PhotoAlbumEditForm(request.POST, instance=instance)
            if form.is_valid():
                album = form.save(commit=False)
                album.save()
                return redirect('album_detail', album=album.slug)
        else:
            form = PhotoAlbumEditForm(instance=instance)
        return render_to_response('photos/album_edit.html',
                                  {'form': form},
                                 context_instance=RequestContext(request))
    raise Http404

@login_required
def photo_add(request, album):
    try:
        album = PhotoAlbum.objects.get(slug=album)
    except:
        raise Http404

    if request.user == album.user:
        if album.size >= settings.PHOTO_ALBUM_LIMIT:
            return render_to_response('photos/album_limit.html',
                                      { 'album': album },
                                     context_instance=RequestContext(request))
        initial = { 'album': album.pk }
        if request.method == 'POST':
            form = PhotoAddForm(request.POST, request.FILES,
                               initial=initial)
            if form.is_valid():
                photo = form.save(commit=False)
                photo.save()
                return redirect('photo_detail', album=album.slug, id=photo.id)
        else:
            form = PhotoAddForm(initial=initial)

        return render_to_response('photos/photo_add.html',
                                  { 'form': form },
                                 context_instance=RequestContext(request))
    raise Http404

@login_required
def photo_edit(request, album, id):
    try:
        album = PhotoAlbum.objects.get(slug=album)
        photo = Photo.objects.get(id=int(id), album=album)
    except:
        raise Http404
    if request.user == album.user:
        instance = photo
        if request.method == 'POST':
            form = PhotoEditForm(request.POST, instance=instance)
            if form.is_valid():
                photo = form.save(commit=False)
                photo.save()
                return redirect('photo_detail', album=album.slug, id=photo.id)
        else:
            form = PhotoEditForm(instance=instance)
        return render_to_response('photos/photo_edit.html',
                                  {'form': form},
                                 context_instance=RequestContext(request))
    raise Http404

def photo_delete_context(request, album, id):
    try:
        album = PhotoAlbum.objects.get(slug=album)
    except:
        raise Http404
    photo = get_object_or_404(Photo, album=album, id=int(id))
    return RequestContext(request, { 'photo': photo })

@login_required
@confirm_required('photos/photo_delete_confirm.html', photo_delete_context)
def photo_delete(request, album, id):
    try:
        album = PhotoAlbum.objects.get(slug=album)
    except:
        raise Http404
    photo = get_object_or_404(Photo, album=album, id=int(id))
    if request.user == photo.album.user:
        photo.delete()
        return redirect('album_detail', album=album.slug)
    raise Http404
