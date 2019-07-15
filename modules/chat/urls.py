from django.conf.urls.defaults import *
from chat.models import ChatRoom
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

room_list = {
    'queryset':ChatRoom.objects.all(),
    'template_name': 'chat/room_list.html',
    'template_object_name': 'room'
}

urlpatterns = patterns('',
    url(r'^$', login_required(object_list),
        room_list, name='room_list'),
    url(r'^create/$', 'chat.views.create_room', name = 'create_room'),
    url(r'^delete/(?P<id>\d+)/$', 'chat.views.delete_room', name = 'delete_room'),
    url(r'^(?P<obj_id>\d+)/$', 'chat.views.chat_room', name = 'chat_room'),
    url(r'^bkend/', include('jchat.urls')),
    )
