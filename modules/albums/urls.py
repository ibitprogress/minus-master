from django.conf.urls.defaults import *

from djangoratings.views import AddRatingFromModel

urlpatterns = patterns('albums.views',
    url(r'^create_album/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/$', 'create_album', name = "create_album"),
    url(r'^upload/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<album>[-\.\w\d]+)/$', 'up_object', name = "up_object_to_album"),
    url(r'^upload/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/$', 'up_object', name = "up_object"),
    url(r'^list/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<album>[-\.\w\d]+)/$', 'show_objects', name = "show_objects_album"),
    url(r'^list/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/$', 'show_objects', name = "show_objects"),
    url(r'^edit/(?P<type>\w+)/(?P<instance_pk>\d+)$', 'edit_object', name = "edit_object"),
    url(r'^edit_album/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<instance_pk>\d+)$', 'edit_album', name = "edit_album"),
    url(r'^remove/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<instance_pk>\d+)$', 'remove_object', name = "remove_object"),
    url(r'^remove_album/(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<instance_pk>\d+)$', 'remove_album', name = "remove_album"),
    url(r'^(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<slug>[-\.\w\d]+)/$', 'show_album',
        name='show_album'),
    url(r'^(?P<type>\w+)/(?P<username>[-\.\w\d]+)/$', 'list_albums',
        name='list_albums'),
    url(r'^(?P<type>\w+)/(?P<username>[-\.\w\d]+)/(?P<slug>[-\.\w\d]+)/(?P<instance_pk>\d+)/$', 'show_object_detail',
        name='show_object_detail'),

    )

urlpatterns += patterns('',
    url(r'rate/(?P<object_id>\d+)/(?P<score>\d+)/', AddRatingFromModel(), {
        'app_label': 'albums',
        'model': 'audio',
        'field_name': 'rating',
    }, name='rate_on_audio'),
)
