from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<hash>\w+)/(?P<id>\d+)/$', 'delivery.views.delivery_detail',
        name='delivery_detail'),
    url(r'^add/$', 'delivery.views.delivery_add', name='delivery_add')
)
