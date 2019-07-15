# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from tastypie.api import Api

from hitcount.views import update_hit_count_ajax

from minusstore.forms import MinusSearchForm
from minusstore.feeds import LatestArivals
from minusstore.api import MinusRecordResource, MinusAuthorResouce, MinusWeekStatsResource

v1_api = Api(api_name='v1')
v1_api.register(MinusRecordResource())
v1_api.register(MinusAuthorResouce())
v1_api.register(MinusWeekStatsResource())


feeds = {
    'latest': LatestArivals,
}

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^minus/', include('minusstore.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^$', 'news.views.news_index'),
    url(r'^blurb/', include('blurbs.urls')),
    url(r'^contest/', include('vocal_contest.urls')),
    url(r'', include('registration.backends.default.urls')),
    url(r'^messages/', include('messages.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^forum/', include('forum.urls')),
    url(r'^friendship/', include('friends.urls')),
    url(r'^photo/', include('photos.urls')),
    url(r'^video/', include('videos.urls')),
    url(r'^albums/', include('albums.urls')),
    url(r'^search/', include('haystack.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^links/', include('links.urls'),{'form_class':MinusSearchForm}),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^delivery/', include('delivery.urls')),
    url(r'^radio/', include('radio.urls')),

    url(r'^chat/', include('chat.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name = "feeds"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    (r'^api/', include(v1_api.urls)),

    url(r'^ajax/hit/$',
        update_hit_count_ajax,
        name='hitcount_update_ajax'),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
)
