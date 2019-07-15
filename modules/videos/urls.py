from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'videos.views.video_album_index',
        name='video_album_index'),
    url(r'^(?P<video_album>[-\.\w\d]+)/$', 'videos.views.video_album_detail',
        name='video_album_detail'),
    url(r'^(?P<video_album>[-\.\w\d]+)/edit/$', 'videos.views.video_album_edit',
        name='video_album_edit'),
    url(r'^(?P<video_album>[-\.\w\d]+)/add/$', 'videos.views.video_add',
        name='video_add'),
    url(r'(?P<video_album>[-\.\w\d]+)/(?P<id>\d+)/$', 'videos.views.video_detail',
        name='video_detail'),
    url(r'(?P<video_album>[-\.\w\d]+)/(?P<id>\d+)/edit/$', 'videos.views.video_edit',
        name='video_edit'),
    url(r'(?P<video_album>[-\.\w\d]+)/(?P<id>\d+)/delete/$', 'videos.views.video_delete',
        name='video_delete'),
)
