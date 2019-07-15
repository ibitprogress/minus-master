# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from forum.decorators import confirm_required

from videos.models import VideoAlbum, Video
from videos.forms import VideoAlbumEditForm, VideoAddForm, VideoEditForm

def video_album_detail(request, video_album):
    video_album = get_object_or_404(VideoAlbum, slug=video_album)
    return render_to_response('videos/video_album_detail.html',
                              {'video_album': video_album},
                             context_instance=RequestContext(request))

def video_detail(request, video_album, id):
    video_album = get_object_or_404(VideoAlbum, slug=video_album)
    video = get_object_or_404(Video, id=int(id), video_album=video_album)
    
    return render_to_response('videos/video_detail.html',
                              {'video': video},
                             context_instance=RequestContext(request))

def video_album_index(request):
    video_albums = VideoAlbum.video_albums.all()
    return render_to_response('videos/video_album_index.html',
                              {'video_albums': video_albums },
                             context_instance=RequestContext(request))

@login_required
def video_album_edit(request, video_album):
    try:
        video_album = VideoAlbum.objects.get(slug=video_album)
    except:
        raise Http404
    if request.user == video_album.user:
        instance = video_album
        if request.method == 'POST':
            form = VideoAlbumEditForm(request.POST, instance=instance)
            if form.is_valid():
                video_album = form.save(commit=False)
                video_album.save()
                return redirect('video_album_detail', video_album=video_album.slug)
        else:
            form = VideoAlbumEditForm(instance=instance)
        return render_to_response('videos/video_album_edit.html',
                                  {'form': form},
                                 context_instance=RequestContext(request))
    raise Http404

@login_required
def video_add(request, video_album):
    try:
        video_album = VideoAlbum.objects.get(slug=video_album)
    except:
        raise Http404

    if request.user == video_album.user:
        initial = {'video_album': video_album.pk}
        if request.method == 'POST':
            form = VideoAddForm(request.POST, initial=initial)
            if form.is_valid():
                video = form.save(commit=False)
                video.save()
                return redirect('video_detail', video_album=video_album.slug,
                                id=video.id)
        else:
            form = VideoAddForm(initial=initial)

        return render_to_response('videos/video_add.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))
    raise Http404

@login_required
def video_edit(request, video_album, id):
    try:
        video_album = VideoAlbum.objects.get(slug=video_album)
        video = Video.objects.get(id=int(id), video_album=video_album)
    except:
        raise Http404
    if request.user == video_album.user:
        instance = video
        if request.method == 'POST':
            form = VideoEditForm(request.POST, instance=instance)
            if form.is_valid():
                video = form.save(commit=False)
                video.save()
                return redirect('video_detail', video_album=video_album.slug,
                                id=video.id)
        else:
            form = VideoEditForm(instance=instance)
        return render_to_response('videos/video_edit.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))
    raise Http404

def video_delete_context(request, video_album, id):
    try:
        video_album = VideoAlbum.objects.get(slug=video_album)
    except:
        raise Http404
    video = get_object_or_404(Video, video_album=video_album, id=int(id))
    return RequestContext(request, {'video': video})

@login_required
@confirm_required('videos/video_delete_confirm.html', video_delete_context)
def video_delete(request, video_album, id):
    try:
        video_album = VideoAlbum.objects.get(slug=video_album)
    except:
        raise Http404
    video = get_object_or_404(Video, video_album=video_album, id=int(id))
    if request.user == video.video_album.user:
        video.delete()
        return redirect('video_album_detail', video_album=video_album.slug)
    raise Http404
