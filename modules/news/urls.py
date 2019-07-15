from django.conf.urls.defaults import *


urlpatterns = patterns('news.views',
    url(r'^$', 'news_index', name='news_index'),
    url(r'^(?P<id>\d+)/$', 'news_detail', name='news_detail'),
    url(r'^add/$','news_add', name = 'news_add'),
    url(r'^edit/(?P<id>\d+)/$','news_edit', name = 'news_edit'),
    url(r'^delete/(?P<id>\d+)/$','news_delete', name = 'news_delete'),
    )
