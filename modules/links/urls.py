from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'links.views.links_list', name='links_list'),
    url(r'^add/$', 'links.views.links_add', name='links_add'),
)
