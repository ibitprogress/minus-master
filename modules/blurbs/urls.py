from django.conf.urls.defaults import *


urlpatterns = patterns('blurbs.views',
    url(r'^(?P<category>[-\.\w\d]+)/(?P<buysell>[B]|[S]|[A])/(?P<id>\d+)$', 'blurb_detail', name='blurb_detail'),
    url(r'^$', 'blurbs_filter', name='blurbs_filter'),
    url(r'^add/$','blurb_add', name = 'blurb_add'),
    url(r'^edit/(?P<id>\d+)/$','blurb_edit', name = 'blurb_edit'),
    url(r'^delete/(?P<id>\d+)/$','blurb_delete', name = 'blurb_delete'),
    url(r'^geo/(?P<id>\d+)/$','geoinfo', name = 'geoinfo'),
    url(r'^up/(?P<id>\d+)/$','blurb_up', name = 'blurb_up'),
    url(r'^user/(?P<username>[-\.\w\d]+)/$','blurbs_by_user', name = 'blurbs_by_user'),

    )

