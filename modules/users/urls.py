from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.views.generic.list_detail import object_list, object_detail
from users.models import UserProfile

from voting.views import vote_on_object
from django.views.decorators.cache import cache_page, never_cache

""""
Definitions for user list and detail objects
TODO write managers to show only necessary
users
"""
user_list = {
    'queryset': User.objects.all(),
    'template_name': 'users/user_list.html',
    'template_object_name': 'user'
}

user_profile = {
    'queryset': User.objects.all(),
    'slug_field': 'username',
    'template_name': 'users/user_profile.html',
    'template_object_name': 'userdetail'
}

user_dict = {
    'model': User,
    'slug_field': 'username',
    'template_name': 'users/user_profile.html',
    'template_object_name': 'userdetail',
    'allow_xmlhttprequest': True,
}

urlpatterns = patterns('users.views',
    url(r'^search/$', 'search', name='user_list_search'),
    url(r'^qlogin/$', 'quick_login', name = 'quick_login'),
    url(r'^block/(?P<id>\d+)/$', 'ban_user', name = 'ban_user'),
    url(r'^submit_staff_ticket/$', 'submit_staff_ticket', name = 'submit_staff_ticket'),
    url(r'^(?P<username>[-\.\w\d]+)/edit/$', 'user_editprofile', name='user_editprofile'),
    url(r'^(?P<username>[-\.\w\d]+)/avatar/$', 'get_avatar',
        name='get_avatar'),
)

urlpatterns += patterns('',
    url('^$', cache_page(object_list, 60*20),
        user_list, name='user_list'),
    url('^(?P<slug>[-\.\w\d]+)/$',
        cache_page(object_detail, 60*10),
        user_profile, name='user_profile'),
    url(r'^(?P<slug>[-\.\w\d]+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, user_dict, name='vote_on_user')
    )

skip_last_activity_date = [
]
