from django.conf.urls.defaults import *

from voting.views import vote_on_object
from photos.models import Photo


urlpatterns = patterns('',
    url(r'^$',
        'photos.views.album_index',
        name='album_index'),
    url(r'^(?P<album>[-\.\w\d]+)/$',
        'photos.views.album_detail',
        name='album_detail'),
    url(r'^(?P<album>[-\.\w\d]+)/edit/$',
        'photos.views.album_edit',
        name='album_edit'),
    url(r'^(?P<album>[-\.\w\d]+)/add/$',
        'photos.views.photo_add',
        name='photo_add'),
    url(r'^(?P<album>[-\.\w\d]+)/(?P<id>\d+)/$',
        'photos.views.photo_detail',
        name='photo_detail'),
    url(r'^(?P<album>[-\.\w\d]+)/(?P<id>\d+)/edit/$',
        'photos.views.photo_edit',
        name='photo_edit'),
    url(r'^(?P<album>[-\.\w\d]+)/(?P<id>\d+)/delete/$',
        'photos.views.photo_delete',
        name='photo_delete'),
)

photo_dict = {
    'model': Photo,
    'slug_field': 'id',
    'template_name': 'photos/photo_detail.html',
    'template_object_name': 'photo',
    'allow_xmlhttprequest': True,
}

urlpatterns += patterns('',
    url(r'^(?P<slug>\w+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, photo_dict, name='vote_on_photo'),                       
)
